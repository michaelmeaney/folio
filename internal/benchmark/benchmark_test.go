package benchmark

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

func TestHelperProcess(t *testing.T) {
	if os.Getenv("FOLIO_HELPER") != "1" {
		return
	}
	args := os.Args
	idx := 0
	for i, arg := range args {
		if arg == "--" {
			idx = i + 1
			break
		}
	}
	if idx == 0 {
		os.Exit(90)
	}
	switch args[idx] {
	case "generate":
		b, _ := os.ReadFile(os.Getenv("FOLIO_PROMPT"))
		_ = b
		fmt.Print("generation diagnostic")
		fmt.Fprint(os.Stderr, "stderr diagnostic")
		_ = os.WriteFile("generated.txt", []byte("isolated fixture"), 0644)
	case "fail":
		fmt.Fprintln(os.Stderr, "expected failure")
		os.Exit(7)
	case "hang":
		time.Sleep(30 * time.Second)
	case "spawn":
		cmd := exec.Command(os.Args[0], "-test.run=TestHelperProcess", "--", "hang")
		cmd.Env = os.Environ()
		_ = cmd.Start()
		fmt.Println(cmd.Process.Pid)
		time.Sleep(30 * time.Second)
	case "protocol":
		var in EvaluationInput
		if err := json.NewDecoder(os.Stdin).Decode(&in); err != nil || in.SchemaVersion != 1 {
			os.Exit(8)
		}
		fmt.Print(`{"schemaVersion":1,"status":"pass","score":0.9}`)
	case "malformed":
		fmt.Print("not JSON")
	case "secret":
		secret := os.Getenv("CHILD_SECRET")
		fmt.Print(secret[:3])
		time.Sleep(10 * time.Millisecond)
		fmt.Print(secret[3:])
		fmt.Fprint(os.Stderr, secret)
	case "environment":
		if os.Getenv("NOT_ALLOWED") != "" {
			os.Exit(9)
		}
		fmt.Print(os.Getenv("CHILD_SECRET"))
	}
	os.Exit(0)
}
func helper(mode string) Command {
	return Command{Argv: []string{os.Args[0], "-test.run=TestHelperProcess", "--", mode}, Environment: map[string]string{"FOLIO_HELPER": "FOLIO_HELPER"}}
}
func fixture(t *testing.T) *Loaded {
	t.Helper()
	t.Setenv("FOLIO_HELPER", "1")
	root := t.TempDir()
	plugin := filepath.Join(root, "plugin")
	for _, dir := range []string{filepath.Join(plugin, ".codex-plugin"), filepath.Join(plugin, "skills/folio/references")} {
		if err := os.MkdirAll(dir, 0755); err != nil {
			t.Fatal(err)
		}
	}
	writeJSON(filepath.Join(plugin, ".codex-plugin/plugin.json"), map[string]string{"name": "folio", "version": "test"})
	os.WriteFile(filepath.Join(plugin, "skills/folio/SKILL.md"), []byte("test"), 0644)
	os.WriteFile(filepath.Join(plugin, "skills/folio/references/acceptance.md"), []byte("test"), 0644)
	os.WriteFile(filepath.Join(root, "reference.png"), []byte("synthetic"), 0644)
	os.WriteFile(filepath.Join(root, "prompt.md"), []byte("test brief"), 0644)
	sha, _ := fileHash(filepath.Join(root, "reference.png"))
	ref, _ := json.Marshal(map[string]any{"file": "reference.png", "sha256": sha, "width": 16, "height": 9, "facts": []any{}, "textBlocks": []any{}})
	c := Case{ID: "test-001", Mode: "quick", Slides: 1, Prompt: "prompt.md", Category: "test"}
	conf := Config{SchemaVersion: 1, Suite: "suite.json", PluginRoot: "plugin", Output: "runs", Controls: Controls{Model: "synthetic", Effort: "none", Surface: "test", Context: "fresh", Repetitions: 4, TimeoutSeconds: 3}, Executor: "generation", Commands: map[string]Command{"generation": helper("generate")}, Evaluators: map[string]EvaluatorConfig{"files": {Kind: "files", Version: "1", Files: []string{"generated.txt"}}}, CaseEvaluators: map[string][]string{"test-001": {"files"}}, Categories: map[string]string{"test-001": "test"}}
	suite := Suite{SchemaVersion: 1, ID: "test-suite", Version: "1", Reference: "reference.json", Cases: []Case{c}}
	writeJSON(filepath.Join(root, "suite.json"), suite)
	writeJSON(filepath.Join(root, "reference.json"), json.RawMessage(ref))
	writeJSON(filepath.Join(root, "benchmark.json"), conf)
	l, err := Load(filepath.Join(root, "benchmark.json"), true)
	if err != nil {
		t.Fatal(err)
	}
	return l
}
func TestParallelArtifactsAndDeterministicResults(t *testing.T) {
	l := fixture(t)
	run, r, err := Run(context.Background(), l, Options{Parallel: 3})
	if err != nil {
		t.Fatal(err)
	}
	if ExitCode(r) != 0 || len(r.Results) != 4 {
		t.Fatalf("%+v", r)
	}
	for i, item := range r.Results {
		if item.Repetition != i+1 {
			t.Fatal("unstable order")
		}
		path := filepath.Join(run, fmt.Sprintf("artefacts/test-001/r%02d/output/generated.txt", i+1))
		if _, err = os.Stat(path); err != nil {
			t.Fatal(err)
		}
		if len(item.Artifacts) == 0 {
			t.Fatal("missing evidence")
		}
	}
	var m Manifest
	if err = readJSON(filepath.Join(run, "manifest.json"), &m, true); err != nil {
		t.Fatal(err)
	}
	if err = verifyInputs(run, m); err != nil {
		t.Fatal(err)
	}
	os.WriteFile(filepath.Join(run, "inputs/reference.png"), []byte("changed"), 0644)
	if verifyInputs(run, m) == nil {
		t.Fatal("mutation accepted")
	}
}
func TestExecutionFailureAndAssertionFailureDiffer(t *testing.T) {
	l := fixture(t)
	l.Config.Controls.Repetitions = 1
	l.Config.Commands["generation"] = helper("fail")
	_, r, err := Run(context.Background(), l, Options{Parallel: 1})
	if err != nil {
		t.Fatal(err)
	}
	if ExitCode(r) != 3 || r.Results[0].Execution.ExitCode != 7 {
		t.Fatalf("%+v", r)
	}
	l.Config.Commands["generation"] = helper("generate")
	l.Config.Evaluators["files"] = EvaluatorConfig{Kind: "files", Version: "1", Files: []string{"missing.txt"}}
	_, r, err = Run(context.Background(), l, Options{Parallel: 1})
	if err != nil {
		t.Fatal(err)
	}
	if ExitCode(r) != 1 {
		t.Fatalf("expected assertion failure: %+v", r)
	}
}
func TestTimeoutAndCancellationPersist(t *testing.T) {
	l := fixture(t)
	l.Config.Controls.TimeoutSeconds = 1
	l.Config.Controls.Repetitions = 2
	l.Config.Commands["generation"] = helper("hang")
	_, r, err := Run(context.Background(), l, Options{Parallel: 2})
	if err != nil {
		t.Fatal(err)
	}
	if ExitCode(r) != 4 {
		t.Fatalf("%+v", r)
	}
	ctx, cancel := context.WithCancel(context.Background())
	go func() { time.Sleep(50 * time.Millisecond); cancel() }()
	run, r, err := Run(ctx, l, Options{Parallel: 1})
	if err != nil {
		t.Fatal(err)
	}
	if ExitCode(r) != 3 || !r.Cancelled {
		t.Fatal("cancellation lost")
	}
	if _, err = os.Stat(filepath.Join(run, "results.json")); err != nil {
		t.Fatal(err)
	}
}
func TestExternalProtocolAndMalformedResponse(t *testing.T) {
	l := fixture(t)
	l.Config.Controls.Repetitions = 1
	l.CaseEvaluators["test-001"] = []string{"external"}
	l.Config.CaseEvaluators = l.CaseEvaluators
	l.Config.Evaluators = map[string]EvaluatorConfig{"external": {Kind: "external", Version: "1", Command: helper("protocol")}}
	_, r, err := Run(context.Background(), l, Options{Parallel: 1})
	if err != nil {
		t.Fatal(err)
	}
	if ExitCode(r) != 0 || r.Results[0].Score == nil {
		t.Fatalf("%+v", r)
	}
	e := l.Config.Evaluators["external"]
	e.Command = helper("malformed")
	l.Config.Evaluators["external"] = e
	_, r, err = Run(context.Background(), l, Options{Parallel: 1})
	if err != nil {
		t.Fatal(err)
	}
	if ExitCode(r) != 3 {
		t.Fatal("malformed protocol did not error")
	}
}
func TestRedactionAndEnvironment(t *testing.T) {
	t.Setenv("FOLIO_HELPER", "1")
	secret := "sensitive-value-12345"
	t.Setenv("FOLIO_TOKEN", secret)
	t.Setenv("NOT_ALLOWED", "sensitive")
	dir := t.TempDir()
	c := helper("secret")
	c.Environment["CHILD_SECRET"] = "FOLIO_TOKEN"
	p := runProcess(context.Background(), c, nil, dir, dir, "secret", nil, []string{secret}, 3)
	if p.Status != "pass" {
		t.Fatal(p)
	}
	for _, path := range []string{p.Stdout, p.Stderr} {
		b, _ := os.ReadFile(path)
		if strings.Contains(string(b), secret) || !strings.Contains(string(b), "[REDACTED]") {
			t.Fatalf("redaction failure %s", b)
		}
	}
	c.Argv[len(c.Argv)-1] = "environment"
	p = runProcess(context.Background(), c, nil, dir, dir, "env", nil, []string{secret}, 3)
	if p.Status != "pass" {
		t.Fatal("implicit environment leaked")
	}
	var buffer bytes.Buffer
	red := newRedactor(&buffer, []string{secret})
	for _, b := range []byte("prefix " + secret + " suffix") {
		red.Write([]byte{b})
	}
	red.close()
	if strings.Contains(buffer.String(), secret) {
		t.Fatal("chunked secret leaked")
	}
}
func TestValidationAndPathTraversal(t *testing.T) {
	l := fixture(t)
	var config Config
	readJSON(filepath.Join(l.Base, "benchmark.json"), &config, true)
	mutations := []func(*Config){func(c *Config) { c.SchemaVersion = 9 }, func(c *Config) { c.CaseEvaluators["test-001"] = []string{"unknown"} }, func(c *Config) { c.Controls.Repetitions = 0 }}
	for _, change := range mutations {
		copy := l.Config
		raw, _ := json.Marshal(l.Config)
		json.Unmarshal(raw, &copy)
		change(&copy)
		writeJSON(filepath.Join(l.Base, "bad.json"), copy)
		if _, err := Load(filepath.Join(l.Base, "bad.json"), true); err == nil {
			t.Fatal("bad config accepted")
		}
	}
	l.Suite.Cases = append(l.Suite.Cases, l.Suite.Cases[0])
	writeJSON(filepath.Join(l.Base, "suite.json"), l.Suite)
	if _, err := Load(filepath.Join(l.Base, "benchmark.json"), true); err == nil {
		t.Fatal("duplicate ID accepted")
	}
	if _, err := safePath(l.Base, "../escape", false); err == nil {
		t.Fatal("escape accepted")
	}
	if _, err := Select(l, []string{"unknown"}, ""); err == nil {
		t.Fatal("unknown selection accepted")
	}
}
func TestComparisonChangesAndExitPrecedence(t *testing.T) {
	a := Results{BenchmarkSHA256: "same", Results: []Result{{CaseID: "case-001", Repetition: 1, Status: "pass"}}}
	b := a
	b.Results = append([]Result(nil), a.Results...)
	b.Results[0].Status = "fail"
	c, code := Compare(a, b)
	if code != 1 || !c.Regression {
		t.Fatal(c, code)
	}
	b.BenchmarkSHA256 = "changed"
	c, code = Compare(a, b)
	if code != 2 || c.Comparable {
		t.Fatal("structural change treated as regression")
	}
	if ExitCode(Results{Results: []Result{{Status: "fail"}, {Status: "error"}, {Status: "timeout"}}}) != 4 {
		t.Fatal("bad precedence")
	}
}

func TestConfiguredSecretsAbsentFromManifestAndLogs(t *testing.T) {
	l := fixture(t)
	secret := "credential-123456789"
	t.Setenv("TEST_TOKEN", secret)
	c := helper("secret")
	c.Environment["CHILD_SECRET"] = "TEST_TOKEN"
	c.SecretEnvironment = []string{"CHILD_SECRET"}
	c.Argv = append(c.Argv, secret)
	l.Config.Commands["generation"] = c
	l.Config.Controls.Repetitions = 1
	if err := writeJSON(filepath.Join(l.Base, "secret.json"), l.Config); err != nil {
		t.Fatal(err)
	}
	l, err := Load(filepath.Join(l.Base, "secret.json"), true)
	if err != nil {
		t.Fatal(err)
	}
	run, _, err := Run(context.Background(), l, Options{Parallel: 1})
	if err != nil {
		t.Fatal(err)
	}
	err = filepath.WalkDir(run, func(path string, d os.DirEntry, err error) error {
		if err != nil {
			return err
		}
		if d.IsDir() {
			return nil
		}
		if strings.HasSuffix(path, ".json") || strings.HasSuffix(path, ".log") {
			data, e := os.ReadFile(path)
			if e != nil {
				return e
			}
			if bytes.Contains(data, []byte(secret)) {
				return fmt.Errorf("secret persisted in %s", path)
			}
		}
		return nil
	})
	if err != nil {
		t.Fatal(err)
	}
}
