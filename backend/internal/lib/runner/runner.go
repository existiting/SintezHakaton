package runner

import (
	"bufio"
	"bytes"
	"context"
	"fmt"
	"os/exec"
)

func New(pythonBin string, scriptPath string, redisRepo RedisWriter) Runner {
	return Runner{
		pythonBin:  pythonBin,
		scriptPath: scriptPath,
		RedisRepo:  redisRepo,
	}
}

func (r *Runner) Run(ctx context.Context, p Params) error {
	const op = "runner.Run"

	cmd := exec.CommandContext(
		ctx,
		r.pythonBin,
		r.scriptPath,
		"--prompt", p.Prompt,
	)

	stdout, err := cmd.StdoutPipe()
	if err != nil {
		return err
	}

	var stderr bytes.Buffer
	cmd.Stderr = &stderr

	if err := cmd.Start(); err != nil {
		return fmt.Errorf("%s: start %w", op, err)
	}

	isWrite := false

	scanner := bufio.NewScanner(stdout)
	for scanner.Scan() {
		line := scanner.Text()

		fmt.Printf("Line: %q | isWrite: %t\n", line, isWrite)

		switch line {
		case "__READY__":
			isWrite = true
			continue
		}

		if !isWrite {
			continue
		}

		if err := r.RedisRepo.AppendChunk(ctx, p.RequestID, line); err != nil {
			return fmt.Errorf("%s: append chunk: %w", op, err)
		}
	}

	if err := r.RedisRepo.AppendChunk(ctx, p.RequestID, "__DONE__"); err != nil {
		return fmt.Errorf("%s: append chunk: %w", op, err)
	}

	if err := cmd.Wait(); err != nil {
		return fmt.Errorf("%s: %w, stderr: %s", op, err, stderr.String())
	}

	return nil
}
