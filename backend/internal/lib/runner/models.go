package runner

import (
	"context"
)

type RedisWriter interface {
	AppendChunk(ctx context.Context, requestID string, line string) error
}

type Runner struct {
	scriptPath string
	pythonBin  string
	RedisRepo  RedisWriter
}

type Params struct {
	RequestID string
	Prompt    string
}

type Result struct {
	Output string
}
