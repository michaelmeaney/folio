// Deterministic generation stub for CI orchestration tests only.
package main

import (
	"io"
	"os"
)

func main() {
	_, _ = io.Copy(io.Discard, os.Stdin)
	if err := os.WriteFile("generated.txt", []byte("synthetic harness fixture\n"), 0644); err != nil {
		panic(err)
	}
}
