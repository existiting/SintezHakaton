package request

import (
	"errors"
	"log/slog"
	"net/http"

	"api/localai/internal/domains"
	"api/localai/internal/lib/api/response"
	"api/localai/internal/lib/logger/sl"
	"api/localai/internal/lib/ws"
	"api/localai/internal/repository"
	"api/localai/internal/service"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/render"
	"github.com/redis/go-redis/v9"
)

type Handler struct {
	src       service.RequestService
	redisRepo repository.RedisRepository
	log       *slog.Logger
}

func Init(log *slog.Logger, src service.RequestService, redisRepo repository.RedisRepository) *Handler {
	return &Handler{
		log:       log,
		src:       src,
		redisRepo: redisRepo,
	}
}

// @Summary      Create AI Request
// @Tags         request
// @Accept       json
// @Produce      json
// @Param        request body CreateRequest true "Body"
// @Param        Authorization header string true "Authorization token"
// @Success      200 {object} CreateResponse
// @Failure      400 {object} response.Response
// @Failure      500 {object} response.Response
// @Router       /v1/chat/completions/ [post]
func (handler *Handler) Create(w http.ResponseWriter, r *http.Request) {
	const op = "handlers.request.Create"

	log := sl.HandlerLog(handler.log, op, r)

	var req CreateRequest

	err := render.DecodeJSON(r.Body, &req)
	if err != nil {
		const msg = "failed to decode body"

		log.Error(msg, sl.Err(err))

		response.ResponseError(w, r, 422, msg)

		return
	}

	dbRequest, err := handler.src.Create(
		domains.AIRequestCredentials{
			Prompt: req.Messages[0].Content,
		},
		r.Context(),
	)
	if err != nil {
		if errors.Is(err, repository.ErrUniqueKey) {
			const msg = "internal server error"

			log.Error(msg, sl.Err(err))

			response.ResponseError(w, r, 500, msg)

			return
		}

		if errors.Is(err, repository.ErrRateLimit) {
			const msg = "rate limit exceeded"

			log.Debug(msg, sl.Err(err))

			response.ResponseError(w, r, 429, msg)

			return
		}

		const msg = "internal server error"

		log.Error(msg, sl.Err(err))

		response.ResponseError(w, r, 500, msg)

		return
	}

	render.JSON(w, r, CreateResponse{
		response.OK(),
		dbRequest.JobID,
		string(dbRequest.Status),
		req.Stream,
		dbRequest.CreatedAt,
	})
}

// @Summary      Get status of AI Request
// @Tags         request
// @Accept       json
// @Produce      json
// @Param        request_id path string true "path"
// @Param        Authorization header string true "Authorization token"
// @Success      200 {object} GetStatusResponse
// @Failure      400 {object} response.Response
// @Failure      500 {object} response.Response
// @Router       /v1/chat/{request_id}/status [get]
func (handler *Handler) GetStatus(w http.ResponseWriter, r *http.Request) {
	const op = "handlers.request.GetStatus"

	log := sl.HandlerLog(handler.log, op, r)
	_ = log

	jobID := r.PathValue("request_id")

	requestStatus, err := handler.src.GetStatusByJobID(
		jobID,
		r.Context(),
	)
	if err != nil {
		if errors.Is(err, repository.ErrNotFound) {
			const msg = "request not found"

			log.Error(msg, sl.Err(err))

			response.ResponseError(w, r, 404, msg)

			return
		}

		const msg = "internal server error"

		log.Error(msg, sl.Err(err))

		response.ResponseError(w, r, 500, msg)

		return
	}

	render.JSON(w, r, GetStatusResponse{
		response.OK(),
		jobID,
		requestStatus,
	})
}

// @Summary      Get Result of AI Request
// @Tags         request
// @Accept       json
// @Produce      json
// @Param        request_id path string true "path"
// @Param        Authorization header string true "Authorization token"
// @Success      200 {object} GetResultResponse
// @Failure      400 {object} response.Response
// @Failure      500 {object} response.Response
// @Router       /v1/chat/{request_id}/result [get]
func (handler *Handler) GetResult(w http.ResponseWriter, r *http.Request) {
	const op = "handlers.request.GetStatus"

	log := sl.HandlerLog(handler.log, op, r)
	_ = log

	jobID := r.PathValue("request_id")

	log.Info("request_id", slog.String("request_id", jobID))

	requestResult, err := handler.src.GetResultByJobID(
		jobID,
		r.Context(),
	)
	if err != nil {
		if errors.Is(err, repository.ErrNotFound) {
			const msg = "request not found"

			log.Error(msg, sl.Err(err))

			response.ResponseError(w, r, 404, msg)

			return
		}

		const msg = "internal server error"

		log.Error(msg, sl.Err(err))

		response.ResponseError(w, r, 500, msg)

		return
	}

	render.JSON(w, r, GetResultResponse{
		Response: response.OK(),
		JobID:    jobID,
		Status:   "completed",
		Result: []Result{
			{
				Role:    "assistant",
				Content: requestResult,
			},
		},
	})
}

func (handler *Handler) StreamResult(w http.ResponseWriter, r *http.Request) {
	const op = "handlers.request.StreamResult"

	log := sl.HandlerLog(handler.log, op, r)

	jobID := chi.URLParam(r, "request_id")
	ctx := r.Context()

	w.Header().Set("Content-Type", "application/x-ndjson")
	w.Header().Set("Cache-Control", "no-cache")
	w.Header().Set("X-Accel-Buffering", "no")

	flusher, ok := w.(http.Flusher)
	if !ok {
		http.Error(w, "streaming not supported", http.StatusInternalServerError)
		return
	}

	// START
	if err := ws.WriteEvent(w, flusher, ws.StreamEvent{
		Event:     "start",
		RequestID: jobID,
	}); err != nil {
		return
	}

	lastID := "0"
	sequence := 0

	for {
		if ctx.Err() != nil {
			return
		}

		entries, err := handler.redisRepo.ReadResultStream(
			ctx,
			jobID,
			lastID,
		)

		if ctx.Err() != nil {
			return
		}

		if err == redis.Nil {
			continue
		}

		if err != nil {
			log.Error("failed to read result stream",
				slog.String("error", err.Error()),
			)
			return
		}

		for _, entry := range entries {
			lastID = entry.ID

			rawToken, ok := entry.Values["token"]
			if !ok || rawToken == nil {
				continue
			}

			token, ok := rawToken.(string)
			if !ok {
				log.Error("invalid redis token type",
					slog.String("entry_id", entry.ID),
				)
				continue
			}

			// COMPLETED
			if token == "__DONE__" {
				event := ws.StreamEvent{
					Event: "completed",
					Usage: &ws.Usage{
						PromptTokens:     12,
						CompletionTokens: sequence,
					},
				}

				if err := ws.WriteEvent(w, flusher, event); err != nil {
					return
				}

				return
			}

			// TOKEN
			sequence++

			if err := ws.WriteEvent(w, flusher, ws.StreamEvent{
				Event:    "token",
				Sequence: sequence,
				Data:     token,
			}); err != nil {
				return
			}
		}
	}
}
