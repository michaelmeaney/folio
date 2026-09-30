package benchmark

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"math"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strings"
)

var identifier = regexp.MustCompile(`^[a-zA-Z0-9][a-zA-Z0-9_-]{0,95}$`)

func readJSON(path string, value any, strict bool) error {
	data, err := os.ReadFile(path)
	if err != nil {
		return err
	}
	return decodeJSON(data, value, strict, path)
}
func decodeJSON(data []byte, value any, strict bool, path string) error {
	d := json.NewDecoder(bytes.NewReader(data))
	if strict {
		d.DisallowUnknownFields()
	}
	if err := d.Decode(value); err != nil {
		return fmt.Errorf("%s: %w", path, err)
	}
	if d.Decode(new(any)) != io.EOF {
		return fmt.Errorf("%s: trailing JSON", path)
	}
	return nil
}
func hash(data []byte) string              { sum := sha256.Sum256(data); return hex.EncodeToString(sum[:]) }
func fileHash(path string) (string, error) { data, err := os.ReadFile(path); return hash(data), err }
func jsonHash(v any) string                { b, _ := json.Marshal(v); return hash(b) }
func writeJSON(path string, v any) error {
	data, err := json.MarshalIndent(v, "", "  ")
	if err != nil {
		return err
	}
	// Persist atomically so an interrupted coordinator does not leave partial JSON.
	tmp, err := os.CreateTemp(filepath.Dir(path), ".record-*")
	if err != nil {
		return err
	}
	name := tmp.Name()
	defer os.Remove(name)
	if _, err = tmp.Write(append(data, '\n')); err != nil {
		tmp.Close()
		return err
	}
	if err = tmp.Close(); err != nil {
		return err
	}
	return os.Rename(name, path)
}
func inside(root, path string) bool {
	rel, err := filepath.Rel(root, path)
	return err == nil && rel != ".." && !strings.HasPrefix(rel, ".."+string(filepath.Separator))
}
func safePath(root, rel string, exists bool) (string, error) {
	if filepath.IsAbs(rel) || (strings.Contains(rel, `\`) || strings.Contains(rel, ":")) {
		return "", fmt.Errorf("path must be relative: %s", rel)
	}
	path := filepath.Join(root, filepath.FromSlash(rel))
	if !inside(root, path) {
		return "", fmt.Errorf("path escapes root: %s", rel)
	}
	if exists {
		actual, err := filepath.EvalSymlinks(path)
		if err != nil {
			return "", err
		}
		canonicalRoot, rootErr := filepath.EvalSymlinks(root)
		if rootErr != nil {
			return "", rootErr
		}
		if !inside(canonicalRoot, actual) {
			return "", fmt.Errorf("symlink escapes root: %s", rel)
		}
		info, err := os.Stat(path)
		if err != nil || !info.Mode().IsRegular() {
			return "", fmt.Errorf("not a regular file: %s", rel)
		}
	}
	return path, nil
}
func resolve(base, path string) string {
	if !filepath.IsAbs(path) {
		path = filepath.Join(base, path)
	}
	abs, _ := filepath.Abs(path)
	return abs
}
func validateCommand(c Command) error {
	if len(c.Argv) == 0 || c.Argv[0] == "" {
		return fmt.Errorf("empty command argv")
	}
	if c.TimeoutSeconds < 0 {
		return fmt.Errorf("negative command timeout")
	}
	for name, parent := range c.Environment {
		if !regexp.MustCompile(`^[A-Za-z_][A-Za-z0-9_]*$`).MatchString(name) || !regexp.MustCompile(`^[A-Za-z_][A-Za-z0-9_]*$`).MatchString(parent) {
			return fmt.Errorf("invalid environment mapping")
		}
	}
	for _, child := range c.SecretEnvironment {
		if _, ok := c.Environment[child]; !ok {
			return fmt.Errorf("secretEnvironment must name an explicitly mapped child variable")
		}
	}
	return nil
}
func Load(configPath string, requireReference bool) (*Loaded, error) {
	configPath = resolve(".", configPath)
	base := filepath.Dir(configPath)
	var c Config
	if err := readJSON(configPath, &c, true); err != nil {
		return nil, err
	}
	if c.SchemaVersion != 1 {
		return nil, fmt.Errorf("unsupported configuration schema version")
	}
	if c.Controls.Context != "fresh" || c.Controls.Repetitions < 1 || c.Controls.Repetitions > 10 || c.Controls.TimeoutSeconds < 1 || c.Controls.Model == "" || c.Controls.Effort == "" || c.Controls.Surface == "" {
		return nil, fmt.Errorf("explicit fresh-context model/effort/surface, repetitions 1..10 and timeout are required")
	}
	if c.Comparison.MaxScoreDrop < 0 || math.IsNaN(c.Comparison.MaxScoreDrop) {
		return nil, fmt.Errorf("invalid score regression threshold")
	}
	var suite Suite
	suitePath := resolve(base, c.Suite)
	if err := readJSON(suitePath, &suite, false); err != nil {
		return nil, err
	}
	if suite.SchemaVersion != 1 || suite.Version == "" || !identifier.MatchString(suite.ID) || len(suite.Cases) == 0 {
		return nil, fmt.Errorf("unsupported or empty suite")
	}
	root := filepath.Dir(suitePath)
	var reference json.RawMessage
	refMeta, err := safePath(root, suite.Reference, true)
	if err != nil {
		return nil, err
	}
	if err = readJSON(refMeta, &reference, false); err != nil {
		return nil, err
	}
	var ref struct {
		File   string `json:"file"`
		SHA    string `json:"sha256"`
		Width  int    `json:"width"`
		Height int    `json:"height"`
	}
	if err = json.Unmarshal(reference, &ref); err != nil || len(ref.SHA) != 64 || ref.Width <= 0 || ref.Height <= 0 {
		return nil, fmt.Errorf("invalid reference metadata")
	}
	refPath := resolve(root, ref.File)
	if c.Reference != "" {
		refPath = resolve(base, c.Reference)
	} else if _, err = safePath(root, ref.File, false); err != nil {
		return nil, err
	}
	if requireReference {
		sha, e := fileHash(refPath)
		if e != nil {
			return nil, e
		}
		if sha != ref.SHA {
			return nil, fmt.Errorf("source reference hash differs from answer key")
		}
	}
	plugin := resolve(base, c.PluginRoot)
	var pkg struct {
		Name    string `json:"name"`
		Version string `json:"version"`
	}
	if err = readJSON(filepath.Join(plugin, ".codex-plugin/plugin.json"), &pkg, false); err != nil {
		return nil, err
	}
	if pkg.Name != "folio" || pkg.Version == "" {
		return nil, fmt.Errorf("invalid Folio plugin")
	}
	if _, err = safePath(plugin, "skills/folio/SKILL.md", true); err != nil {
		return nil, err
	}
	l := &Loaded{Config: c, Suite: suite, Reference: reference, ReferencePath: refPath, Base: base, SuiteRoot: root, Plugin: plugin, CaseEvaluators: map[string][]string{}}
	for name, command := range c.Commands {
		if !identifier.MatchString(name) {
			return nil, fmt.Errorf("invalid command name")
		}
		if err = validateCommand(command); err != nil {
			return nil, fmt.Errorf("command %s: %w", name, err)
		}
		for _, child := range command.SecretEnvironment {
			parent := command.Environment[child]
			if value := os.Getenv(parent); value != "" {
				l.Secrets = append(l.Secrets, value)
			}
		}
	}
	if _, ok := c.Commands[c.Executor]; !ok {
		return nil, fmt.Errorf("unknown executor %s", c.Executor)
	}
	if c.Reviewer != "" {
		if _, ok := c.Commands[c.Reviewer]; !ok {
			return nil, fmt.Errorf("unknown reviewer")
		}
	}
	for name, e := range c.Evaluators {
		if !identifier.MatchString(name) || e.Version == "" {
			return nil, fmt.Errorf("invalid evaluator identity/version")
		}
		switch e.Kind {
		case "external":
			if err = validateCommand(e.Command); err != nil {
				return nil, err
			}
		case "files":
			if len(e.Files) == 0 {
				return nil, fmt.Errorf("empty file assertions")
			}
		default:
			return nil, fmt.Errorf("unknown evaluator kind %s", e.Kind)
		}
		for _, rel := range e.Files {
			if _, err = safePath(root, rel, false); err != nil {
				return nil, err
			}
		}
		for _, rel := range e.Resources {
			if _, err = safePath(base, rel, true); err != nil {
				return nil, err
			}
		}
		for _, child := range e.Command.SecretEnvironment {
			parent := e.Command.Environment[child]
			if value := os.Getenv(parent); value != "" {
				l.Secrets = append(l.Secrets, value)
			}
		}
	}
	seen := map[string]bool{}
	for i := range l.Suite.Cases {
		item := &l.Suite.Cases[i]
		if !identifier.MatchString(item.ID) || seen[item.ID] {
			return nil, fmt.Errorf("invalid or duplicate case ID %s", item.ID)
		}
		seen[item.ID] = true
		if item.Slides < 1 || !map[string]bool{"quick": true, "guided": true, "governed": true}[item.Mode] {
			return nil, fmt.Errorf("invalid mode/slide count for %s", item.ID)
		}
		if _, err = safePath(root, item.Prompt, true); err != nil {
			return nil, err
		}
		item.Category = c.Categories[item.ID]
		if item.Category == "" {
			item.Category = item.Mode
		}
		if !identifier.MatchString(item.Category) {
			return nil, fmt.Errorf("invalid category")
		}
		names := c.CaseEvaluators[item.ID]
		if len(names) == 0 {
			return nil, fmt.Errorf("case %s has no evaluators", item.ID)
		}
		evalSeen := map[string]bool{}
		for _, name := range names {
			if _, ok := c.Evaluators[name]; !ok || evalSeen[name] {
				return nil, fmt.Errorf("unknown or duplicate evaluator %s", name)
			}
			evalSeen[name] = true
		}
		l.CaseEvaluators[item.ID] = names
	}
	for id := range c.CaseEvaluators {
		if !seen[id] {
			return nil, fmt.Errorf("evaluator mapping references unknown case %s", id)
		}
	}
	sort.Slice(l.Suite.Cases, func(i, j int) bool { return l.Suite.Cases[i].ID < l.Suite.Cases[j].ID })
	return l, nil
}
func Select(l *Loaded, ids []string, category string) ([]Case, error) {
	wanted := map[string]bool{}
	for _, id := range ids {
		wanted[id] = true
	}
	found := map[string]bool{}
	var cases []Case
	for _, c := range l.Suite.Cases {
		if (len(ids) == 0 || wanted[c.ID]) && (category == "" || c.Category == category) {
			cases = append(cases, c)
			found[c.ID] = true
		}
	}
	for id := range wanted {
		if !found[id] {
			return nil, fmt.Errorf("unknown or excluded case %s", id)
		}
	}
	if len(cases) == 0 {
		return nil, fmt.Errorf("empty case selection")
	}
	return cases, nil
}

func sanitizeJSON(data []byte, secrets []string) ([]byte, error) {
	var value any
	d := json.NewDecoder(bytes.NewReader(data))
	d.UseNumber()
	if err := d.Decode(&value); err != nil {
		return nil, err
	}
	var clean func(any) any
	clean = func(v any) any {
		switch item := v.(type) {
		case string:
			return redact(item, secrets)
		case []any:
			for i, x := range item {
				item[i] = clean(x)
			}
		case map[string]any:
			for k, x := range item {
				item[k] = clean(x)
			}
		}
		return v
	}
	return json.Marshal(clean(value))
}
