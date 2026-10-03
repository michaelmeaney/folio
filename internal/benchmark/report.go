package benchmark

import (
	"encoding/json"
	"fmt"
	"html/template"
	"io"
	"os"
	"path/filepath"
	"sort"
)

func LoadResults(path string) (Results, error) {
	var r Results
	if err := readJSON(path, &r, true); err != nil {
		return r, err
	}
	if r.SchemaVersion != 1 || len(r.Results) == 0 {
		return r, fmt.Errorf("invalid results schema or empty results")
	}
	seen := map[string]bool{}
	for _, item := range r.Results {
		key := fmt.Sprintf("%s/%d", item.CaseID, item.Repetition)
		if !identifier.MatchString(item.CaseID) || item.Repetition < 1 || seen[key] || !map[string]bool{"pass": true, "fail": true, "error": true, "timeout": true, "skipped": true, "unverified": true}[item.Status] {
			return r, fmt.Errorf("invalid or duplicate result")
		}
		seen[key] = true
	}
	return r, nil
}
func Summary(w io.Writer, r Results) {
	counts := map[string]int{}
	for _, item := range r.Results {
		counts[item.Status]++
		fmt.Fprintf(w, "%-10s %-28s r%02d %.3fs\n", item.Status, item.CaseID, item.Repetition, item.DurationSeconds)
	}
	fmt.Fprintf(w, "%d passed, %d failed, %d errors, %d timed out, %d unverified, %d skipped\n", counts["pass"], counts["fail"], counts["error"], counts["timeout"], counts["unverified"], counts["skipped"])
}
func Report(path, output string, w io.Writer) error {
	r, err := LoadResults(path)
	if err != nil {
		return err
	}
	Summary(w, r)
	if output == "" {
		return nil
	}
	type row struct {
		Result
		Images []string
		Deck   string
	}
	rows := []row{}
	for _, item := range r.Results {
		rr := row{Result: item}
		for _, a := range item.Artifacts {
			if _, err = safePath(filepath.Dir(path), a.Path, false); err != nil {
				return err
			}
			if filepath.Ext(a.Path) == ".png" {
				rr.Images = append(rr.Images, a.Path)
			}
			if filepath.Base(a.Path) == "deck.pptx" {
				rr.Deck = a.Path
			}
		}
		rows = append(rows, rr)
	}
	// URLs are relative to results.json; write HTML beside it to keep artifact links portable.
	if resolve(".", filepath.Dir(output)) != resolve(".", filepath.Dir(path)) {
		return fmt.Errorf("write HTML beside results.json so artifact links remain valid")
	}
	t := template.Must(template.New("report").Parse(`<!doctype html><html><head><meta charset="utf-8"><title>Folio benchmark</title><style>body{font:16px system-ui;max-width:1200px;margin:40px auto;padding:0 24px}img{width:100%;height:auto}section{margin:32px 0;border-top:1px solid #bbb}pre{white-space:pre-wrap}</style></head><body><h1>Folio benchmark {{.RunID}}</h1>{{range .Rows}}<section><h2>{{.CaseID}} r{{.Repetition}}: {{.Status}}</h2><p>{{.DurationSeconds}}s · {{.Diagnostic}}</p>{{if .Deck}}<a href="{{.Deck}}">PowerPoint</a>{{end}}{{range .Images}}<img src="{{.}}" alt="Benchmark render">{{end}}<ul>{{range .Violations}}<li>{{.ID}}: {{.Message}}</li>{{end}}</ul></section>{{end}}</body></html>`))
	file, err := os.Create(output)
	if err != nil {
		return err
	}
	defer file.Close()
	return t.Execute(file, map[string]any{"RunID": r.RunID, "Rows": rows})
}

type Delta struct {
	CaseID               string             `json:"caseId"`
	Repetition           int                `json:"repetition"`
	Before               string             `json:"before,omitempty"`
	After                string             `json:"after,omitempty"`
	Change               string             `json:"change"`
	DurationDelta        float64            `json:"durationDeltaSeconds"`
	ScoreDelta           *float64           `json:"scoreDelta,omitempty"`
	ViolationsBefore     []Violation        `json:"violationsBefore,omitempty"`
	ViolationsAfter      []Violation        `json:"violationsAfter,omitempty"`
	EvaluatorScoreDeltas map[string]float64 `json:"evaluatorScoreDeltas,omitempty"`
}
type Comparison struct {
	Comparable bool    `json:"comparable"`
	Reason     string  `json:"reason,omitempty"`
	Regression bool    `json:"regression"`
	Deltas     []Delta `json:"deltas"`
}

func Compare(a, b Results) (Comparison, int) {
	out := Comparison{Comparable: a.BenchmarkSHA256 == b.BenchmarkSHA256 && jsonHash(a.Controls) == jsonHash(b.Controls) && jsonHash(a.Comparison) == jsonHash(b.Comparison)}
	if !out.Comparable {
		out.Reason = "benchmark definitions, evaluator versions, controls or comparison policy changed"
	}
	left, right := map[string]Result{}, map[string]Result{}
	keys := map[string]bool{}
	for _, r := range a.Results {
		k := fmt.Sprintf("%s/%02d", r.CaseID, r.Repetition)
		left[k] = r
		keys[k] = true
	}
	for _, r := range b.Results {
		k := fmt.Sprintf("%s/%02d", r.CaseID, r.Repetition)
		right[k] = r
		keys[k] = true
	}
	sorted := []string{}
	for k := range keys {
		sorted = append(sorted, k)
	}
	sort.Strings(sorted)
	incomplete := false
	for _, key := range sorted {
		x, xok := left[key]
		y, yok := right[key]
		d := Delta{Before: x.Status, After: y.Status, CaseID: y.CaseID, Repetition: y.Repetition, Change: "unchanged", ViolationsBefore: x.Violations, ViolationsAfter: y.Violations, EvaluatorScoreDeltas: map[string]float64{}}
		if !xok {
			d.Change = "added"
			out.Comparable = false
			out.Reason = "case set changed"
		} else if !yok {
			d.CaseID = x.CaseID
			d.Repetition = x.Repetition
			d.Change = "missing"
			out.Comparable = false
			out.Reason = "case set changed"
		} else {
			d.DurationDelta = y.DurationSeconds - x.DurationSeconds
			if x.Status != y.Status {
				d.Change = "status-changed"
			}
			if x.Status == "pass" && y.Status != "pass" {
				out.Regression = true
				d.Change = "newly-failing"
			}
			if x.Status != "pass" && y.Status == "pass" {
				d.Change = "newly-passing"
			}
			if x.Score != nil && y.Score != nil {
				delta := *y.Score - *x.Score
				d.ScoreDelta = &delta
				if delta < -b.Comparison.MaxScoreDrop {
					out.Regression = true
				}
			}
			for name, ev := range y.Evaluations {
				old, ok := x.Evaluations[name]
				if !ok {
					out.Comparable = false
					out.Reason = "evaluator set changed"
					continue
				}
				if ev.Score != nil && old.Score != nil {
					delta := *ev.Score - *old.Score
					d.EvaluatorScoreDeltas[name] = delta
					if delta < -b.Comparison.MaxScoreDrop {
						out.Regression = true
					}
				}
				if (len(ev.Runtime) > 0 && string(ev.Runtime) != "null") || (len(old.Runtime) > 0 && string(old.Runtime) != "null") {
					var curr, prev any
					_ = json.Unmarshal(ev.Runtime, &curr)
					_ = json.Unmarshal(old.Runtime, &prev)
					if jsonHash(curr) != jsonHash(prev) {
						out.Comparable = false
						out.Reason = "actual model/renderer/application profiles changed"
					}
				}
			}
			if len(x.Evaluations) != len(y.Evaluations) {
				out.Comparable = false
				out.Reason = "evaluator set changed"
			}
		}
		if x.Status == "skipped" || x.Status == "unverified" || y.Status == "skipped" || y.Status == "unverified" {
			incomplete = true
		}
		out.Deltas = append(out.Deltas, d)
	}
	if !out.Comparable {
		return out, 2
	}
	if incomplete {
		out.Reason = "complete review required"
		return out, 3
	}
	if code := ExitCode(b); code == 4 || code == 3 {
		return out, code
	}
	if out.Regression {
		return out, 1
	}
	return out, 0
}
