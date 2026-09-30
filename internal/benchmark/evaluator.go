package benchmark

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
)

type externalEvaluator struct {
	name    string
	config  EvaluatorConfig
	secrets []string
}

func (e externalEvaluator) Name() string { return e.name }
func (e externalEvaluator) Evaluate(ctx context.Context, input EvaluationInput) (EvaluationResult, Process, error) {
	data, err := json.Marshal(input)
	if err != nil {
		return EvaluationResult{}, Process{}, err
	}
	vars := values(input)
	vars["resources"] = filepath.Join(input.RunDirectory, "inputs/evaluators", e.name)
	p := runProcess(ctx, e.config.Command, data, input.TrialDirectory, filepath.Join(input.TrialDirectory, "logs"), "evaluator-"+e.name, vars, e.secrets, input.Controls.TimeoutSeconds)
	if p.Status != "pass" {
		return EvaluationResult{}, p, fmt.Errorf("evaluator %s: %s", e.name, p.Status)
	}
	if len(p.response) > 10*1024*1024 {
		return EvaluationResult{}, p, fmt.Errorf("evaluator response exceeds 10 MiB")
	}
	clean, err := sanitizeJSON(p.response, e.secrets)
	if err != nil {
		return EvaluationResult{}, p, err
	}

	var result EvaluationResult
	if err = decodeJSON(clean, &result, true, "evaluator response"); err != nil {
		return result, p, err
	}
	if result.SchemaVersion != 1 || !map[string]bool{"pass": true, "fail": true, "error": true, "timeout": true, "skipped": true, "unverified": true}[result.Status] {
		return result, p, fmt.Errorf("invalid evaluator result schema/status")
	}
	return result, p, nil
}

type fileEvaluator struct {
	name  string
	files []string
}

func (e fileEvaluator) Name() string { return e.name }
func (e fileEvaluator) Evaluate(ctx context.Context, input EvaluationInput) (EvaluationResult, Process, error) {
	result := EvaluationResult{SchemaVersion: 1, Status: "pass"}
	for _, name := range e.files {
		if err := ctx.Err(); err != nil {
			return result, Process{}, err
		}
		p, err := safePath(filepath.Join(input.TrialDirectory, "output"), name, true)
		if err != nil {
			result.Status = "fail"
			result.Violations = append(result.Violations, Violation{ID: "missing-file", Message: name + ": " + err.Error()})
			continue
		}
		info, _ := os.Stat(p)
		if info.Size() == 0 {
			result.Status = "fail"
			result.Violations = append(result.Violations, Violation{ID: "empty-file", Message: name})
		}
	}
	return result, Process{Status: "pass"}, nil
}
func values(input EvaluationInput) map[string]string {
	return map[string]string{"config": input.ConfigurationDirectory, "model": input.Controls.Model, "effort": input.Controls.Effort, "surface": input.Controls.Surface, "prompt": filepath.Join(input.TrialDirectory, "prompt.md"), "review_prompt": filepath.Join(input.TrialDirectory, "review-prompt.md"), "reference": filepath.Join(input.RunDirectory, "inputs/reference.png"), "plugin": filepath.Join(input.RunDirectory, "inputs/plugin"), "output": filepath.Join(input.TrialDirectory, "output"), "run": input.RunDirectory, "trial": input.TrialDirectory}
}
