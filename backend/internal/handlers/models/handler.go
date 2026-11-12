package ping

import (
	"log/slog"
	"net/http"

	"api/localai/internal/lib/api/response"

	"github.com/go-chi/render"
)

type Model struct {
	Name string `json:"name"`
}

type ModelsResponse struct {
	response.Response
	Models []Model `json:"models"`
}

type Handler struct {
	log *slog.Logger
}

func Init(log *slog.Logger) *Handler {
	return &Handler{
		log: log,
	}
}

// @Summary      Get models
// @Tags         request
// @Success      200 {object} ModelsResponse
// @Router       /v1/models [get]
// @Summary      Get Result of AI Request
// @Tags         request
// @Param        Authorization header string true "Authorization token"
func (handler *Handler) GetModels(w http.ResponseWriter, r *http.Request) {
	const op = "handlers.health.Health"

	render.JSON(w, r, ModelsResponse{
		Models: []Model{
			{
				Name: "v1",
			},
		},
	})
}
