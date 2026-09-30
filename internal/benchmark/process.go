package benchmark

import (
	"bytes"
	"context"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"sort"
	"strings"
	"sync"
	"time"
)

// Keep enough trailing bytes to redact secrets split across writes.
type redactor struct {
	mu      sync.Mutex
	out     io.Writer
	secrets []string
	pending string
	keep    int
}

func newRedactor(out io.Writer, secrets []string) *redactor {
	r := &redactor{out: out, secrets: secrets}
	for _, s := range secrets {
		if len(s) > r.keep {
			r.keep = len(s)
		}
	}
	return r
}
func redact(s string, secrets []string) string {
	ordered := append([]string(nil), secrets...)
	sort.Slice(ordered, func(i, j int) bool { return len(ordered[i]) > len(ordered[j]) })
	for _, secret := range ordered {
		if secret != "" {
			s = strings.ReplaceAll(s, secret, "[REDACTED]")
		}
	}
	return s
}
func (r *redactor) Write(p []byte) (int, error) {
	r.mu.Lock()
	defer r.mu.Unlock()
	r.pending += string(p)
	// Redact complete matches before keeping the suffix, so a replacement cannot be split and leak.
	r.pending = redact(r.pending, r.secrets)
	n := len(r.pending) - r.keep
	if n > 0 {
		_, err := io.WriteString(r.out, r.pending[:n])
		r.pending = r.pending[n:]
		return len(p), err
	}
	return len(p), nil
}
func (r *redactor) close() error {
	r.mu.Lock()
	defer r.mu.Unlock()
	_, err := io.WriteString(r.out, redact(r.pending, r.secrets))
	r.pending = ""
	return err
}
func environment(mapping map[string]string) []string {
	env := []string{}
	for _, key := range []string{"PATH", "HOME", "USERPROFILE", "SYSTEMROOT", "WINDIR", "TMPDIR", "TEMP", "TMP", "LANG", "LC_ALL"} {
		if v, ok := os.LookupEnv(key); ok {
			env = append(env, key+"="+v)
		}
	}
	keys := make([]string, 0, len(mapping))
	for key := range mapping {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	for _, key := range keys {
		env = append(env, key+"="+os.Getenv(mapping[key]))
	}
	return env
}
func expand(argv []string, values map[string]string) []string {
	out := append([]string(nil), argv...)
	for i, arg := range out {
		for key, value := range values {
			arg = strings.ReplaceAll(arg, "{"+key+"}", value)
		}
		out[i] = arg
	}
	return out
}
func runProcess(parent context.Context, command Command, stdin []byte, cwd, logDir, prefix string, values map[string]string, secrets []string, defaultTimeout int) Process {
	start := time.Now()
	result := Process{StartedAt: time.Now().UTC().Format(time.RFC3339Nano), Status: "error", ExitCode: -1, Stdout: filepath.ToSlash(filepath.Join(logDir, prefix+".stdout.log")), Stderr: filepath.ToSlash(filepath.Join(logDir, prefix+".stderr.log"))}

	if err := os.MkdirAll(logDir, 0755); err != nil {
		result.Diagnostic = err.Error()
		return result
	}
	stdout, err := os.Create(result.Stdout)
	if err != nil {
		result.Diagnostic = err.Error()
		return result
	}
	defer stdout.Close()
	stderr, err := os.Create(result.Stderr)
	if err != nil {
		result.Diagnostic = err.Error()
		return result
	}
	defer stderr.Close()
	out, errOut := newRedactor(stdout, secrets), newRedactor(stderr, secrets)
	timeout := command.TimeoutSeconds
	if timeout == 0 {
		timeout = defaultTimeout
	}
	ctx, cancel := context.WithTimeout(parent, time.Duration(timeout)*time.Second)
	defer cancel()
	argv := expand(command.Argv, values)
	result.Command = append([]string(nil), argv...)
	for i, arg := range result.Command {
		result.Command[i] = redact(arg, secrets)
	}
	// Commands come only from the validated trusted operator registry, never fixture text or case argv.
	// Dynamic argv is the explicit executor boundary; no shell is inserted.
	cmd := exec.CommandContext(ctx, argv[0], argv[1:]...) // nosemgrep: go.lang.security.audit.dangerous-exec-command.dangerous-exec-command
	cmd.Dir = cwd
	cmd.Env = environment(command.Environment)
	cmd.Stdin = strings.NewReader(string(stdin))
	capture := &boundedBuffer{limit: 10*1024*1024 + 1}
	cmd.Stdout = io.MultiWriter(out, capture)
	cmd.Stderr = errOut
	cmd.WaitDelay = 2 * time.Second
	configureProcess(cmd)
	err = cmd.Run()
	cleanupProcess(cmd)
	flushErr := out.close()
	if e := errOut.close(); flushErr == nil {
		flushErr = e
	}
	result.response = append([]byte(nil), capture.Bytes()...)
	result.EndedAt = time.Now().UTC().Format(time.RFC3339Nano)
	result.DurationSeconds = time.Since(start).Seconds()
	if cmd.ProcessState != nil {
		result.ExitCode = cmd.ProcessState.ExitCode()
	}
	switch {
	case ctx.Err() == context.DeadlineExceeded:
		result.Status = "timeout"
		result.Diagnostic = "process timeout"
	case parent.Err() != nil:
		result.Status = "skipped"
		result.Diagnostic = "cancelled"
	case err != nil:
		result.Diagnostic = redact(fmt.Sprint(err), secrets)
	case flushErr != nil:
		result.Diagnostic = flushErr.Error()
	default:
		result.Status = "pass"
	}
	return result
}

// Evaluator protocol bytes stay in bounded memory; only redacted logs reach disk.
type boundedBuffer struct {
	bytes.Buffer
	limit int
}

func (b *boundedBuffer) Write(p []byte) (int, error) {
	n := len(p)
	room := b.limit - b.Len()
	if room > 0 {
		keep := len(p)
		if keep > room {
			keep = room
		}
		_, _ = b.Buffer.Write(p[:keep])
	}
	return n, nil
}
