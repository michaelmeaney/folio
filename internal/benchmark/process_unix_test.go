//go:build !windows

package benchmark

import (
	"context"
	"os"
	"strconv"
	"strings"
	"syscall"
	"testing"
	"time"
)

func TestTimeoutKillsDescendant(t *testing.T) {
	t.Setenv("FOLIO_HELPER", "1")
	dir := t.TempDir()
	p := runProcess(context.Background(), helper("spawn"), nil, dir, dir, "spawn", nil, nil, 1)
	if p.Status != "timeout" {
		t.Fatal(p)
	}
	data, err := os.ReadFile(p.Stdout)
	if err != nil {
		t.Fatal(err)
	}
	pid, err := strconv.Atoi(strings.TrimSpace(string(data)))
	if err != nil {
		t.Fatal(err)
	}
	deadline := time.Now().Add(2 * time.Second)
	for time.Now().Before(deadline) {
		err = syscall.Kill(pid, 0)
		if err == syscall.ESRCH {
			return
		}
		time.Sleep(20 * time.Millisecond)
	}
	// Linux may retain a reparented zombie until PID 1 reaps it: it is terminated, not running.
	if state, err := os.ReadFile("/proc/" + strconv.Itoa(pid) + "/stat"); err == nil && strings.Contains(string(state), ") Z ") {
		return
	}
	t.Fatalf("descendant %d survived process group cancellation", pid)
}
