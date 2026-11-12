package ping

import (
	"log/slog"
	"net/http"

	"api/localai/internal/lib/api/response"

	"github.com/go-chi/render"
)

type HealthResponse struct {
	response.Response
	Health string `json:"health"`
}

type Handler struct {
	log *slog.Logger
}

func Init(log *slog.Logger) *Handler {
	return &Handler{
		log: log,
	}
}

// @Summary      Health check
// @Tags         Health
// @Success      200 {object} HealthResponse
// @Router       /health [get]
func (handler *Handler) Health(w http.ResponseWriter, r *http.Request) {
	const op = "handlers.health.Health"

	render.JSON(w, r, HealthResponse{
		Health: "OK",
	})
}
