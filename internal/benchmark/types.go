// Package benchmark orchestrates trusted commands; evaluators own presentation judgment.
package benchmark

import (
	"context"
	"encoding/json"
)

const Version = "0.1.0"
const SchemaVersion = 1

type Command struct {
	SecretEnvironment []string          `json:"secretEnvironment,omitempty"`
	Argv              []string          `json:"argv"`
	Environment       map[string]string `json:"environment,omitempty"` // child variable -> parent variable
	TimeoutSeconds    int               `json:"timeoutSeconds,omitempty"`
}
type EvaluatorConfig struct {
	Kind      string   `json:"kind"`
	Version   string   `json:"version"`
	Command   Command  `json:"command,omitempty"`
	Files     []string `json:"files,omitempty"`
	Resources []string `json:"resources,omitempty"`
}
type Controls struct {
	Model          string `json:"model"`
	Effort         string `json:"effort"`
	Surface        string `json:"surface"`
	Context        string `json:"context"`
	DesignSystem   string `json:"designSystem"`
	Repetitions    int    `json:"repetitions"`
	TimeoutSeconds int    `json:"timeoutSeconds"`
}
type Policy struct {
	MaxScoreDrop float64 `json:"maxScoreDrop"`
}
type Config struct {
	SchemaVersion  int                        `json:"schemaVersion"`
	Suite          string                     `json:"suite"`
	PluginRoot     string                     `json:"pluginRoot"`
	Reference      string                     `json:"reference,omitempty"`
	Output         string                     `json:"output"`
	Controls       Controls                   `json:"controls"`
	Commands       map[string]Command         `json:"commands"`
	Executor       string                     `json:"executor"`
	Reviewer       string                     `json:"reviewer,omitempty"`
	Evaluators     map[string]EvaluatorConfig `json:"evaluators"`
	CaseEvaluators map[string][]string        `json:"caseEvaluators"`
	Categories     map[string]string          `json:"categories"`
	Comparison     Policy                     `json:"comparison"`
}
type Criterion struct {
	ID          string `json:"id"`
	Gate        string `json:"gate"`
	Description string `json:"description"`
}
type Case struct {
	ID        string      `json:"id"`
	Name      string      `json:"name,omitempty"`
	Category  string      `json:"category,omitempty"`
	Mode      string      `json:"mode"`
	Operation string      `json:"operation"`
	Slides    int         `json:"slides"`
	ExactCopy bool        `json:"exactCopy"`
	Prompt    string      `json:"prompt"`
	Criteria  []Criterion `json:"criteria"`
	Tags      []string    `json:"tags,omitempty"`
}
type Suite struct {
	SchemaVersion int    `json:"schemaVersion"`
	ID            string `json:"id"`
	Version       string `json:"version"`
	Reference     string `json:"reference"`
	Cases         []Case `json:"cases"`
}
type Loaded struct {
	Config                  Config
	Suite                   Suite
	Reference               json.RawMessage
	ReferencePath           string
	Base, SuiteRoot, Plugin string
	CaseEvaluators          map[string][]string
	Secrets                 []string
}
type Violation struct {
	ID      string `json:"id"`
	Message string `json:"message"`
}
type Artifact struct {
	Path   string `json:"path"`
	SHA256 string `json:"sha256"`
	Size   int64  `json:"size"`
}
type Process struct {
	StartedAt       string   `json:"startedAt,omitempty"`
	EndedAt         string   `json:"endedAt,omitempty"`
	Command         []string `json:"command,omitempty"`
	response        []byte
	Status          string  `json:"status"`
	DurationSeconds float64 `json:"durationSeconds"`
	ExitCode        int     `json:"exitCode"`
	Stdout          string  `json:"stdout"`
	Stderr          string  `json:"stderr"`
	Diagnostic      string  `json:"diagnostic,omitempty"`
}
type EvaluationInput struct {
	ConfigurationDirectory string          `json:"configurationDirectory"`
	SchemaVersion          int             `json:"schemaVersion"`
	RunDirectory           string          `json:"runDirectory"`
	TrialDirectory         string          `json:"trialDirectory"`
	TrialPath              string          `json:"trialPath"`
	Case                   Case            `json:"case"`
	Reference              json.RawMessage `json:"reference"`
	Controls               Controls        `json:"controls"`
	SystemCanvas           []float64       `json:"systemCanvas"`
}
type EvaluationResult struct {
	SchemaVersion int             `json:"schemaVersion"`
	Status        string          `json:"status"`
	Score         *float64        `json:"score,omitempty"`
	Violations    []Violation     `json:"violations,omitempty"`
	Diagnostics   json.RawMessage `json:"diagnostics,omitempty"`
	ContextIDs    []string        `json:"contextIds,omitempty"`
	Runtime       json.RawMessage `json:"runtime,omitempty"`
}
type Evaluator interface {
	Name() string
	Evaluate(context.Context, EvaluationInput) (EvaluationResult, Process, error)
}
type Trial struct {
	CaseID     string `json:"caseId"`
	Repetition int    `json:"repetition"`
	Path       string `json:"path"`
}
type Manifest struct {
	SchemaVersion   int               `json:"schemaVersion"`
	RunID           string            `json:"runId"`
	Timestamp       string            `json:"timestamp"`
	HarnessVersion  string            `json:"folioBenchVersion"`
	FolioVersion    string            `json:"folioVersion"`
	GitCommit       string            `json:"gitCommit,omitempty"`
	GitBranch       string            `json:"gitBranch,omitempty"`
	OS              string            `json:"operatingSystem"`
	Arch            string            `json:"architecture"`
	SuiteID         string            `json:"suiteId"`
	SuiteVersion    string            `json:"suiteVersion"`
	BenchmarkSHA256 string            `json:"benchmarkSha256"`
	PluginSHA256    string            `json:"pluginSha256"`
	Configuration   Config            `json:"configuration"`
	SelectedCases   []string          `json:"selectedCases"`
	Parallelism     int               `json:"parallelism"`
	Inputs          map[string]string `json:"inputs"`
	Trials          []Trial           `json:"trials"`
	SystemCanvas    []float64         `json:"systemCanvas"`
}
type Result struct {
	EvaluatorProcesses map[string]Process          `json:"evaluatorProcesses,omitempty"`
	CaseID             string                      `json:"caseId"`
	Repetition         int                         `json:"repetition"`
	Status             string                      `json:"status"`
	DurationSeconds    float64                     `json:"durationSeconds"`
	Score              *float64                    `json:"score,omitempty"`
	Violations         []Violation                 `json:"violations,omitempty"`
	Artifacts          []Artifact                  `json:"artifacts,omitempty"`
	Execution          Process                     `json:"execution"`
	Review             *Process                    `json:"review,omitempty"`
	Evaluations        map[string]EvaluationResult `json:"evaluations"`
	Diagnostic         string                      `json:"diagnostic,omitempty"`
}
type Results struct {
	SchemaVersion   int      `json:"schemaVersion"`
	ManifestSHA256  string   `json:"manifestSha256"`
	RunID           string   `json:"runId"`
	CompletedAt     string   `json:"completedAt"`
	BenchmarkSHA256 string   `json:"benchmarkSha256"`
	Controls        Controls `json:"controls"`
	Comparison      Policy   `json:"comparison"`
	Results         []Result `json:"results"`
	Cancelled       bool     `json:"cancelled"`
}

func ExitCode(results Results) int {
	if results.Cancelled {
		return 3
	}
	code := 0
	for _, r := range results.Results {
		switch r.Status {
		case "timeout":
			return 4
		case "error", "unverified", "skipped":
			code = 3
		case "fail":
			if code == 0 {
				code = 1
			}
		}
	}
	return code
}
