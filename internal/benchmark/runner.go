package benchmark

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
	"sync"
	"time"
)

type Options struct {
	Progress func(Result)
	Output   string
	Parallel int
	Cases    []string
	Category string
	Verbose  bool
}

func canvas(plugin, system string) ([]float64, error) {
	var registry struct {
		Systems []struct {
			ID       string `json:"id"`
			Manifest string `json:"manifest"`
		} `json:"systems"`
	}
	root := filepath.Join(plugin, "design-systems")
	if err := readJSON(filepath.Join(root, "registry.json"), &registry, false); err != nil {
		return nil, err
	}
	for _, entry := range registry.Systems {
		if entry.ID != system {
			continue
		}
		manifestPath, err := safePath(root, entry.Manifest, true)
		if err != nil {
			return nil, err
		}
		var manifest struct {
			Tokens    string            `json:"tokens"`
			Resources map[string]string `json:"resources"`
		}
		if err = readJSON(manifestPath, &manifest, false); err != nil {
			return nil, err
		}
		rel := manifest.Resources["presentation"]
		modern := rel != ""
		if !modern {
			rel = manifest.Tokens
		}
		p, err := safePath(filepath.Dir(manifestPath), rel, true)
		if err != nil {
			return nil, err
		}
		var values struct {
			Canvas struct {
				Width    float64 `json:"width"`
				Height   float64 `json:"height"`
				WidthIn  float64 `json:"widthIn"`
				HeightIn float64 `json:"heightIn"`
			} `json:"canvas"`
		}
		if err = readJSON(p, &values, false); err != nil {
			return nil, err
		}
		w, h := values.Canvas.Width, values.Canvas.Height
		if !modern {
			w, h = values.Canvas.WidthIn, values.Canvas.HeightIn
		}
		if w <= 0 || h <= 0 {
			return nil, fmt.Errorf("invalid design-system canvas")
		}
		return []float64{w, h}, nil
	}
	return nil, fmt.Errorf("unregistered system %s", system)
}
func gitValue(root string, args ...string) string {
	argv := append([]string{"-C", root}, args...)
	out, err := exec.Command("git", argv...).Output()
	if err != nil {
		return ""
	}
	return strings.TrimSpace(string(out))
}
func Prepare(l *Loaded, o Options) (string, Manifest, error) {
	var m Manifest
	if o.Parallel < 1 || o.Parallel > 64 {
		return "", m, fmt.Errorf("parallel must be 1..64")
	}
	cases, err := Select(l, o.Cases, o.Category)
	if err != nil {
		return "", m, err
	}
	var systemCanvas []float64
	for _, c := range cases {
		if c.Mode == "governed" {
			systemCanvas, err = canvas(l.Plugin, l.Config.Controls.DesignSystem)
			if err != nil {
				return "", m, err
			}
			break
		}
	}
	output := o.Output
	if output == "" {
		output = resolve(l.Base, l.Config.Output)
	} else {
		output = resolve(".", output)
	}
	if inside(l.Plugin, output) {
		rel, _ := filepath.Rel(l.Plugin, output)
		first := strings.Split(rel, string(filepath.Separator))[0]
		if !excluded[first] {
			return "", m, fmt.Errorf("output inside plugin must be under an excluded directory, e.g. bench/runs")
		}
	}
	if err = os.MkdirAll(output, 0755); err != nil {
		return "", m, err
	}
	idBytes := make([]byte, 6)
	if _, err = rand.Read(idBytes); err != nil {
		return "", m, err
	}
	id := time.Now().UTC().Format("20060102T150405Z") + "-" + hex.EncodeToString(idBytes)
	run := filepath.Join(output, id)
	if err = os.Mkdir(run, 0755); err != nil {
		return "", m, err
	}
	// A partially prepared run is retained if preparation fails, never reused.
	inputs := filepath.Join(run, "inputs")
	if err = os.Mkdir(inputs, 0755); err != nil {
		return run, m, err
	}
	if err = snapshotPlugin(l.Plugin, filepath.Join(inputs, "plugin")); err != nil {
		return run, m, err
	}
	if err = copyFile(l.ReferencePath, filepath.Join(inputs, "reference.png")); err != nil {
		return run, m, err
	}
	if err = writeJSON(filepath.Join(inputs, "reference.json"), l.Reference); err != nil {
		return run, m, err
	}
	if err = writeJSON(filepath.Join(inputs, "suite.json"), l.Suite); err != nil {
		return run, m, err
	}
	frozenConfig := l.Config
	raw, _ := json.Marshal(frozenConfig)
	safeConfig, e := sanitizeJSON(raw, l.Secrets)
	if e != nil {
		return run, m, e
	}
	if err = json.Unmarshal(safeConfig, &frozenConfig); err != nil {
		return run, m, err
	}
	if err = writeJSON(filepath.Join(inputs, "configuration.json"), frozenConfig); err != nil {
		return run, m, err
	}
	promptHashes := map[string]string{}
	evaluatorHashes := map[string]string{}
	for name, e := range l.Config.Evaluators {
		for _, rel := range e.Resources {
			src, _ := safePath(l.Base, rel, true)
			dst := filepath.Join(inputs, "evaluators", name, filepath.FromSlash(rel))
			if err = copyFile(src, dst); err != nil {
				return run, m, err
			}
			sha, _ := fileHash(dst)
			evaluatorHashes[name+"/"+rel] = sha
		}
	}
	for _, c := range cases {
		promptPath, _ := safePath(l.SuiteRoot, c.Prompt, true)
		brief, e := os.ReadFile(promptPath)
		if e != nil {
			return run, m, e
		}
		promptHashes[c.ID] = hash(brief)
		if err = copyFile(promptPath, filepath.Join(inputs, "prompts", c.ID+".md")); err != nil {
			return run, m, err
		}
		for rep := 1; rep <= l.Config.Controls.Repetitions; rep++ {
			rel := fmt.Sprintf("artefacts/%s/r%02d", c.ID, rep)
			trial := filepath.Join(run, filepath.FromSlash(rel))
			if err = os.MkdirAll(filepath.Join(trial, "output"), 0755); err != nil {
				return run, m, err
			}
			instruction := strings.ReplaceAll(string(brief), "{{design_system}}", l.Config.Controls.DesignSystem)
			prompt := fmt.Sprintf("# Folio benchmark %s repetition %d\n\nRead and execute the frozen Skill at %s. Reference image: %s. Output directory: %s.\n\n%s\n\nThe operation, mode, permissions, system where applicable and slide count are confirmed. Start a fresh session with no inherited conversation (Codex: fork_turns=none). Record actual context ID, inheritance, model, effort and runtime in output/execution-notes.md. Do not inspect other trials or the reviewer answer key. Do not modify frozen inputs. Produce output/deck.pptx and actual renders at output/render/slide-01.png etc., at least 1280 pixels wide. Keep source analysis and reconstruction metadata; unavailable measurements remain unobserved. Do not fill review.json. Paths beginning output/ are relative to %s.\n", c.ID, rep, filepath.Join(inputs, "plugin/skills/folio/SKILL.md"), filepath.Join(inputs, "reference.png"), filepath.Join(trial, "output"), instruction, trial)
			reviewPrompt := fmt.Sprintf("# Independent review %s repetition %d\n\nStart a new context with no inherited conversation. Read %s and %s for this case's rubric/answer key; inspect %s and every actual PowerPoint/render under %s. Follow frozen Folio acceptance rules at %s. Fill %s with reviewer identity, verified distinct generation/review context IDs (inheritance none), actual runtime, deck/render hashes and evidence-backed pass/fail/unverified for every criterion and fact. Review visible content, relationships, composition, accessibility and story directly. Open and edit a copy in the named application; unavailable checks remain unverified. Do not accept generator claims as evidence or inspect other trials. Keep review evidence under output/review/.\n", c.ID, rep, filepath.Join(inputs, "suite.json"), filepath.Join(inputs, "reference.json"), filepath.Join(inputs, "reference.png"), filepath.Join(trial, "output"), filepath.Join(inputs, "plugin/skills/folio/references/acceptance.md"), filepath.Join(trial, "review.json"))
			for name, text := range map[string]string{"prompt.md": prompt, "review-prompt.md": reviewPrompt} {
				if err = os.WriteFile(filepath.Join(trial, name), []byte(text), 0644); err != nil {
					return run, m, err
				}
			}
			review := reviewTemplate(c, l.Reference)
			if err = writeJSON(filepath.Join(trial, "review.json"), review); err != nil {
				return run, m, err
			}
			m.Trials = append(m.Trials, Trial{CaseID: c.ID, Repetition: rep, Path: filepath.ToSlash(rel)})
		}
	}
	var pkg struct {
		Version string `json:"version"`
	}
	if err = readJSON(filepath.Join(inputs, "plugin/.codex-plugin/plugin.json"), &pkg, false); err != nil {
		return run, m, err
	}
	m.SchemaVersion = 1
	m.RunID = id
	m.Timestamp = time.Now().UTC().Format(time.RFC3339Nano)
	m.HarnessVersion = Version
	m.FolioVersion = pkg.Version
	m.OS = runtime.GOOS
	m.Arch = runtime.GOARCH
	m.GitCommit = gitValue(l.Plugin, "rev-parse", "HEAD")
	m.GitBranch = gitValue(l.Plugin, "branch", "--show-current")
	m.SuiteID = l.Suite.ID
	m.SuiteVersion = l.Suite.Version
	m.Configuration = frozenConfig
	m.Parallelism = o.Parallel
	m.SystemCanvas = systemCanvas
	for _, c := range cases {
		m.SelectedCases = append(m.SelectedCases, c.ID)
	}
	m.Inputs, err = fileDigests(inputs)
	if err != nil {
		return run, m, err
	}
	pluginHashes, err := fileDigests(filepath.Join(inputs, "plugin"))
	if err != nil {
		return run, m, err
	}
	m.PluginSHA256 = jsonHash(pluginHashes)
	m.BenchmarkSHA256 = jsonHash(map[string]any{"suite": l.Suite, "reference": l.Reference, "prompts": promptHashes, "evaluators": frozenConfig.Evaluators, "resources": evaluatorHashes, "commands": frozenConfig.Commands, "executor": frozenConfig.Executor, "reviewer": frozenConfig.Reviewer, "policy": frozenConfig.Comparison, "harness": Version})
	if err = writeJSON(filepath.Join(run, "manifest.json"), m); err != nil {
		return run, m, err
	}
	return run, m, nil
}
func reviewTemplate(c Case, ref json.RawMessage) map[string]any {
	pending := func() any { return map[string]any{"status": "unverified", "notes": "", "evidence": []any{}} }
	criteria := map[string]any{}
	for _, item := range c.Criteria {
		criteria[item.ID] = pending()
	}
	var source struct {
		Facts []struct {
			ID string `json:"id"`
		} `json:"facts"`
	}
	_ = json.Unmarshal(ref, &source)
	facts := map[string]any{}
	for _, fact := range source.Facts {
		facts[fact.ID] = pending()
	}
	return map[string]any{"reviewer": "", "runtime": map[string]string{"model": "", "effort": "", "surface": "", "renderer": "", "application": ""}, "contexts": map[string]any{"generation": map[string]string{"id": "", "inheritance": ""}, "review": map[string]string{"id": "", "inheritance": ""}}, "deckSha256": "", "renderSha256": map[string]string{}, "criteria": criteria, "facts": facts}
}
func executeTrial(ctx context.Context, l *Loaded, run string, m Manifest, t Trial) Result {
	start := time.Now()
	ctx, cancelTrial := context.WithTimeout(ctx, time.Duration(l.Config.Controls.TimeoutSeconds)*time.Second)
	defer cancelTrial()
	result := Result{CaseID: t.CaseID, Repetition: t.Repetition, Status: "skipped", Evaluations: map[string]EvaluationResult{}, EvaluatorProcesses: map[string]Process{}}
	trial := filepath.Join(run, filepath.FromSlash(t.Path))
	var c Case
	for _, item := range l.Suite.Cases {
		if item.ID == t.CaseID {
			c = item
			break
		}
	}
	input := EvaluationInput{SchemaVersion: 1, ConfigurationDirectory: l.Base, RunDirectory: run, TrialDirectory: trial, TrialPath: t.Path, Case: c, Reference: l.Reference, Controls: l.Config.Controls, SystemCanvas: m.SystemCanvas}
	if ctx.Err() != nil {
		result.Diagnostic = "cancelled before execution"
		return result
	}
	prompt, err := os.ReadFile(filepath.Join(trial, "prompt.md"))
	if err != nil {
		result.Status = "error"
		result.Diagnostic = err.Error()
		return result
	}
	result.Execution = runProcess(ctx, l.Config.Commands[l.Config.Executor], prompt, filepath.Join(trial, "output"), filepath.Join(trial, "logs"), "generation", values(input), l.Secrets, l.Config.Controls.TimeoutSeconds)
	legacyStatus := "failed"
	if result.Execution.Status == "pass" {
		legacyStatus = "completed"
	}
	if err = writeJSON(filepath.Join(trial, "execution.json"), map[string]any{"status": legacyStatus, "elapsedSeconds": result.Execution.DurationSeconds, "exitCode": result.Execution.ExitCode, "timedOut": result.Execution.Status == "timeout"}); err != nil {
		result.Status = "error"
		result.Diagnostic = err.Error()
		return result
	}
	result.Status = result.Execution.Status
	if result.Status == "pass" && l.Config.Reviewer != "" {
		reviewPrompt, e := os.ReadFile(filepath.Join(trial, "review-prompt.md"))
		if e != nil {
			result.Status = "error"
			result.Diagnostic = e.Error()
		} else {
			p := runProcess(ctx, l.Config.Commands[l.Config.Reviewer], reviewPrompt, trial, filepath.Join(trial, "logs"), "review", values(input), l.Secrets, l.Config.Controls.TimeoutSeconds)
			result.Review = &p
			result.Status = p.Status
		}
	}
	// Evaluate failed generation too, to preserve judgment/runtime evidence, except after timeout/cancellation.
	if result.Status != "timeout" && ctx.Err() == nil {
		for _, name := range l.CaseEvaluators[c.ID] {
			e := l.Config.Evaluators[name]
			var evaluator Evaluator
			if e.Kind == "files" {
				evaluator = fileEvaluator{name: name, files: e.Files}
			} else {
				evaluator = externalEvaluator{name: name, config: e, secrets: l.Secrets}
			}
			evaluation, p, eErr := evaluator.Evaluate(ctx, input)
			evaluatorTimedOut := p.Status == "timeout"
			if eErr != nil {
				evaluation = EvaluationResult{SchemaVersion: 1, Status: "error", Violations: []Violation{{ID: "evaluator-error", Message: redact(eErr.Error(), l.Secrets)}}}
				if evaluatorTimedOut {
					evaluation.Status = "timeout"
				}
			}
			for _, field := range []*string{&p.Stdout, &p.Stderr} {
				if *field != "" {
					if rel, e := filepath.Rel(run, *field); e == nil {
						*field = filepath.ToSlash(rel)
					}
				}
			}
			result.EvaluatorProcesses[name] = p
			result.Evaluations[name] = evaluation
			result.Violations = append(result.Violations, evaluation.Violations...)
			result.Status = combineStatus(result.Status, evaluation.Status)
			if evaluation.Score != nil && len(l.CaseEvaluators[c.ID]) == 1 {
				result.Score = evaluation.Score
			}
			if err = writeJSON(filepath.Join(trial, "evaluation-"+name+".json"), evaluation); err != nil {
				result.Status = "error"
				result.Diagnostic = err.Error()
			}
		}
	}
	if ctx.Err() == context.DeadlineExceeded {
		result.Status = "timeout"
	}
	if ctx.Err() != nil && ctx.Err() != context.DeadlineExceeded && result.Status != "timeout" {
		result.Status = "skipped"
		result.Diagnostic = "cancelled"
	}
	result.DurationSeconds = time.Since(start).Seconds()
	result.Artifacts, err = artifacts(run, trial)
	if err != nil {
		result.Status = "error"
		result.Diagnostic = err.Error()
	}
	for _, p := range []*Process{&result.Execution, result.Review} {
		if p != nil {
			if rel, e := filepath.Rel(run, p.Stdout); e == nil {
				p.Stdout = filepath.ToSlash(rel)
			}
			if rel, e := filepath.Rel(run, p.Stderr); e == nil {
				p.Stderr = filepath.ToSlash(rel)
			}
		}
	}
	return result
}
func combineStatus(a, b string) string {
	rank := map[string]int{"pass": 0, "fail": 1, "skipped": 2, "unverified": 3, "error": 4, "timeout": 5}
	if rank[b] > rank[a] {
		return b
	}
	return a
}
func Run(ctx context.Context, l *Loaded, o Options) (string, Results, error) {
	run, m, err := Prepare(l, o)
	if err != nil {
		return run, Results{}, err
	}
	mh, err := fileHash(filepath.Join(run, "manifest.json"))
	if err != nil {
		return run, Results{}, err
	}
	out := Results{SchemaVersion: 1, ManifestSHA256: mh, RunID: m.RunID, BenchmarkSHA256: m.BenchmarkSHA256, Controls: m.Configuration.Controls, Comparison: m.Configuration.Comparison, Results: make([]Result, len(m.Trials))}
	for i, t := range m.Trials {
		out.Results[i] = Result{CaseID: t.CaseID, Repetition: t.Repetition, Status: "skipped", Diagnostic: "pending execution"}
	}
	if err = writeJSON(filepath.Join(run, "results.json"), out); err != nil {
		return run, out, err
	}
	var mu sync.Mutex
	var wg sync.WaitGroup
	errCh := make(chan error, len(m.Trials))
	jobs := make(chan int, len(m.Trials))
	for i := range m.Trials {
		jobs <- i
	}
	close(jobs)
	for worker := 0; worker < o.Parallel; worker++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for i := range jobs {
				r := executeTrial(ctx, l, run, m, m.Trials[i])
				mu.Lock()
				out.Results[i] = r
				if o.Progress != nil {
					o.Progress(r)
				}
				if e := writeJSON(filepath.Join(run, "results.json"), out); e != nil {
					errCh <- e
				}
				mu.Unlock()
			}
		}()
	}
	wg.Wait()
	close(errCh)
	out.Cancelled = ctx.Err() != nil
	out.CompletedAt = time.Now().UTC().Format(time.RFC3339Nano)
	if e := verifyInputs(run, m); e != nil {
		for i := range out.Results {
			out.Results[i].Status = "error"
			out.Results[i].Diagnostic = e.Error()
		}
	}
	contexts := map[string][]int{}
	for i, r := range out.Results {
		for _, e := range r.Evaluations {
			for _, id := range e.ContextIDs {
				if id != "" {
					contexts[id] = append(contexts[id], i)
				}
			}
		}
	}
	for _, indexes := range contexts {
		unique := map[int]bool{}
		for _, i := range indexes {
			unique[i] = true
		}
		if len(unique) > 1 {
			for i := range unique {
				out.Results[i].Status = "fail"
				out.Results[i].Violations = append(out.Results[i].Violations, Violation{ID: "reused-context", Message: "context reused across benchmark trials"})
			}
		}
	}
	if err = writeJSON(filepath.Join(run, "results.json"), out); err != nil {
		return run, out, err
	}
	for e := range errCh {
		if e != nil {
			return run, out, e
		}
	}
	return run, out, nil
}
