package benchmark

import (
	"fmt"
	"io"
	"io/fs"
	"os"
	"path/filepath"
	"strings"
)

var excluded = map[string]bool{".git": true, ".venv": true, "__pycache__": true, "node_modules": true, "bench": true, "runs": true, "outputs": true, "tmp": true, "dist": true, ".DS_Store": true}

func copyFile(source, dest string) error {
	if err := os.MkdirAll(filepath.Dir(dest), 0755); err != nil {
		return err
	}
	in, err := os.Open(source)
	if err != nil {
		return err
	}
	defer in.Close()
	out, err := os.Create(dest)
	if err != nil {
		return err
	}
	_, err = io.Copy(out, in)
	closeErr := out.Close()
	if err != nil {
		return err
	}
	return closeErr
}
func snapshotPlugin(root, dest string) error {
	return filepath.WalkDir(root, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}
		if path == root {
			return os.MkdirAll(dest, 0755)
		}
		if excluded[d.Name()] || strings.HasPrefix(d.Name(), ".env") || strings.HasSuffix(d.Name(), ".pyc") {
			if d.IsDir() {
				return filepath.SkipDir
			}
			return nil
		}
		if d.Type()&os.ModeSymlink != 0 {
			return fmt.Errorf("plugin symlink unsupported: %s", path)
		}
		if d.IsDir() {
			return nil
		}
		if !d.Type().IsRegular() {
			return fmt.Errorf("unsupported plugin entry %s", path)
		}
		rel, _ := filepath.Rel(root, path)
		return copyFile(path, filepath.Join(dest, rel))
	})
}
func fileDigests(root string) (map[string]string, error) {
	out := map[string]string{}
	err := filepath.WalkDir(root, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}
		if d.Type()&os.ModeSymlink != 0 {
			return fmt.Errorf("symlink in frozen inputs")
		}
		if d.IsDir() {
			return nil
		}
		if strings.HasSuffix(d.Name(), ".pyc") {
			return nil
		}
		rel, _ := filepath.Rel(root, path)
		if strings.Contains(filepath.ToSlash(rel), "__pycache__/") {
			return nil
		}
		sha, e := fileHash(path)
		if e != nil {
			return e
		}
		out[filepath.ToSlash(rel)] = sha
		return nil
	})
	return out, err
}
func artifacts(run, trial string) ([]Artifact, error) {
	var out []Artifact
	err := filepath.WalkDir(trial, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}
		if path != trial && (d.Name() == "node_modules" || d.Name() == ".venv" || d.Name() == "__pycache__" || d.Name() == ".git") {
			if d.IsDir() {
				return filepath.SkipDir
			}
			return nil
		}
		if d.Type()&os.ModeSymlink != 0 {
			return fmt.Errorf("artifact symlink unsupported: %s", path)
		}
		if d.IsDir() {
			return nil
		}
		info, err := d.Info()
		if err != nil {
			return err
		}
		sha, err := fileHash(path)
		if err != nil {
			return err
		}
		rel, _ := filepath.Rel(run, path)
		out = append(out, Artifact{Path: filepath.ToSlash(rel), SHA256: sha, Size: info.Size()})
		return nil
	})
	return out, err
}
func verifyInputs(run string, m Manifest) error {
	actual, err := fileDigests(filepath.Join(run, "inputs"))
	if err != nil {
		return err
	}
	if jsonHash(actual) != jsonHash(m.Inputs) {
		return fmt.Errorf("frozen inputs changed during execution")
	}
	return nil
}
