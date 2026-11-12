package ws

import (
	"encoding/json"
	"net/http"
)

func WriteEvent(
	w http.ResponseWriter,
	flusher http.Flusher,
	event StreamEvent,
) error {
	if err := json.NewEncoder(w).Encode(event); err != nil {
		return err
	}

	flusher.Flush()
	return nil
}

type StreamEvent struct {
	Event     string `json:"event"`
	RequestID string `json:"request_id,omitempty"`
	Sequence  int    `json:"sequence,omitempty"`
	Data      string `json:"data,omitempty"`
	Usage     *Usage `json:"usage,omitempty"`
}

type Usage struct {
	PromptTokens     int `json:"prompt_tokens"`
	CompletionTokens int `json:"completion_tokens"`
}
