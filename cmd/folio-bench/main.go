package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"github.com/michaelmeaney/folio/internal/benchmark"
	"os"
	"os/signal"
	"strings"
	"syscall"
)

type stringsFlag []string

func (s *stringsFlag) String() string     { return strings.Join(*s, ",") }
func (s *stringsFlag) Set(v string) error { *s = append(*s, v); return nil }
func main()                               { os.Exit(cli(os.Args[1:])) }
func cli(args []string) int {
	fail := func(err error) int { fmt.Fprintln(os.Stderr, "folio-bench:", err); return 2 }
	if len(args) == 0 {
		return fail(fmt.Errorf("use run, list, validate, compare, report or version"))
	}
	if args[0] == "version" {
		fmt.Printf("folio-bench %s (schema %d)\n", benchmark.Version, benchmark.SchemaVersion)
		return 0
	}
	flags := flag.NewFlagSet(args[0], flag.ContinueOnError)
	config := flags.String("config", "bench/benchmark.json", "trusted configuration JSON")
	jsonOutput := flags.Bool("json", false, "machine-readable stdout")
	output := flags.String("output", "", "run root or HTML report path")
	parallel := flags.Int("parallel", 1, "bounded workers (1..64)")
	category := flags.String("category", "", "case category")
	verbose := flags.Bool("verbose", false, "include diagnostic locations")
	var ids stringsFlag
	flags.Var(&ids, "case", "select case ID; repeatable")
	positionalCategory := ""
	rest := args[1:]
	if args[0] == "run" && len(rest) > 0 && !strings.HasPrefix(rest[0], "-") {
		positionalCategory = rest[0]
		rest = rest[1:]
	}
	if err := flags.Parse(rest); err != nil {
		return 2
	}
	if positionalCategory != "" {
		if *category != "" && *category != positionalCategory {
			return fail(fmt.Errorf("conflicting categories"))
		}
		*category = positionalCategory
	}
	switch args[0] {
	case "list", "validate", "run":
		if len(flags.Args()) != 0 {
			return fail(fmt.Errorf("unexpected positional arguments"))
		}
		l, err := benchmark.Load(*config, args[0] != "list")
		if err != nil {
			return fail(err)
		}
		cases, err := benchmark.Select(l, ids, *category)
		if err != nil {
			return fail(err)
		}
		if args[0] != "list" {
			if err := benchmark.ValidateSelection(l, cases); err != nil {
				return fail(err)
			}
		}
		if args[0] == "validate" {
			if *jsonOutput {
				_ = json.NewEncoder(os.Stdout).Encode(map[string]any{"valid": true, "cases": len(cases), "schemaVersion": 1})
			} else {
				fmt.Printf("Valid benchmark: %d cases\n", len(cases))
			}
			return 0
		}
		if args[0] == "list" {
			if *jsonOutput {
				_ = json.NewEncoder(os.Stdout).Encode(cases)
			} else {
				fmt.Println("CASE                         CATEGORY          EVALUATORS")
				for _, c := range cases {
					fmt.Printf("%-28s %-17s %s\n", c.ID, c.Category, strings.Join(l.CaseEvaluators[c.ID], ", "))
				}
			}
			return 0
		}
		ctx, cancel := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
		defer cancel()
		fmt.Fprintf(os.Stderr, "Running %d cases × %d repetitions with %d workers\n", len(cases), l.Config.Controls.Repetitions, *parallel)
		progress := func(r benchmark.Result) {
			fmt.Fprintf(os.Stderr, "%-10s %-28s r%02d %.3fs\n", r.Status, r.CaseID, r.Repetition, r.DurationSeconds)
		}
		run, results, err := benchmark.Run(ctx, l, benchmark.Options{Progress: progress, Output: *output, Parallel: *parallel, Cases: ids, Category: *category, Verbose: *verbose})
		if err != nil {
			return fail(err)
		}
		if *jsonOutput {
			_ = json.NewEncoder(os.Stdout).Encode(results)
		} else {
			fmt.Printf("Folio Benchmark %s\nRun: %s\n", benchmark.Version, run)
			benchmark.Summary(os.Stdout, results)
			if *verbose {
				for _, r := range results.Results {
					fmt.Printf("%s: %s\n  stdout: %s\n  stderr: %s\n", r.CaseID, r.Diagnostic, r.Execution.Stdout, r.Execution.Stderr)
				}
			}
		}
		return benchmark.ExitCode(results)
	case "report":
		if len(flags.Args()) != 1 {
			return fail(fmt.Errorf("report requires results.json"))
		}
		path := flags.Args()[0]
		if *jsonOutput {
			r, e := benchmark.LoadResults(path)
			if e != nil {
				return fail(e)
			}
			_ = json.NewEncoder(os.Stdout).Encode(r)
			return 0
		}
		if err := benchmark.Report(path, *output, os.Stdout); err != nil {
			return fail(err)
		}
		return 0
	case "compare":
		if len(flags.Args()) != 2 {
			return fail(fmt.Errorf("compare requires baseline and candidate results.json"))
		}
		a, err := benchmark.LoadResults(flags.Args()[0])
		if err != nil {
			return fail(err)
		}
		b, err := benchmark.LoadResults(flags.Args()[1])
		if err != nil {
			return fail(err)
		}
		result, code := benchmark.Compare(a, b)
		_ = json.NewEncoder(os.Stdout).Encode(result)
		return code
	default:
		return fail(fmt.Errorf("unknown command %s", args[0]))
	}
}
