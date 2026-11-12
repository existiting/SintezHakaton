package request

import (
	"log/slog"
	"net/http"

	"api/localai/internal/repository/postgres"
	"api/localai/internal/repository/rabbitmq"
	redisRepo "api/localai/internal/repository/redis"
	"api/localai/internal/service/request"

	"github.com/go-chi/chi/v5"
	"github.com/redis/go-redis/v9"
)

func RouterInit(
	db *postgres.Database,
	slog *slog.Logger,
	redisClient *redis.Client,
	rabbimqClient *rabbitmq.RabbitClient,
) http.Handler {
	repo := postgres.InitRequestRepository(db)

	redisRepo := redisRepo.InitRedisRepo(redisClient)
	rabbitRepo := rabbitmq.InitRabbitRepo(rabbimqClient)
	service := request.Init(repo, redisRepo, rabbitRepo)
	handler := Init(slog, service, redisRepo)

	r := chi.NewRouter()

	r.Post("/completions", handler.Create)
	r.Get("/{request_id}/status", handler.GetStatus)
	r.Get("/{request_id}/ws", handler.StreamResult)
	r.Get("/{request_id}/result", handler.GetResult)

	return r
}
