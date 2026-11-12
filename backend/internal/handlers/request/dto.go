package request

import (
	"time"

	"api/localai/internal/lib/api/response"
)

type GetRequest struct {
	JobID string `json:"prompt" validate:"required,string"`
}

// ======

type Message struct {
	Content string `json:"content" validate:"required,string"`
}

type CreateRequest struct {
	Model    string    `json:"model" validate:"required,string"`
	Messages []Message `json:"messages" validate:"required,min=1,dive"`
	Stream   bool      `json:"stream" validate:"bool"`
}

type CreateResponse struct {
	response.Response
	JobID     string    `json:"request_id"`
	Status    string    `json:"status"`
	Stream    bool      `json:"stream"`
	CreatedAT time.Time `json:"created_at"`
}

// =======

type GetStatusResponse struct {
	response.Response
	JobID  string `json:"request_id"`
	Status string `json:"status"`
}

// =======

type Result struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type GetResultResponse struct {
	response.Response
	JobID  string   `json:"request_id"`
	Status string   `json:"status"`
	Result []Result `json:"result"`
}
