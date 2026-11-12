package handlers

import (
	"log/slog"

	"api/localai/internal/config"
	modelsH "api/localai/internal/handlers/models"
	"api/localai/internal/repository/postgres"
	"api/localai/internal/repository/rabbitmq"
	"api/localai/internal/service/auth"

	ping "api/localai/internal/handlers/health"
	"api/localai/internal/handlers/request"

	mdl "api/localai/internal/handlers/middleware"

	_ "api/localai/docs"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/redis/go-redis/v9"
	httpSwagger "github.com/swaggo/http-swagger"
)

func Init(
	log *slog.Logger,
	db *postgres.Database,
	redisClient *redis.Client,
	rabbitClient *rabbitmq.RabbitClient,
	cfg *config.Config,
) *chi.Mux {
	r := chi.NewRouter()

	r.Use(middleware.Logger)
	r.Use(middleware.RequestID)
	r.Use(middleware.CleanPath)
	r.Use(middleware.Recoverer)
	HealthH := ping.Init(log)
	ModelsH := modelsH.Init(log)

	authRepo := postgres.Init(db)
	authService := auth.Init(authRepo)

	requestRouter := request.RouterInit(
		db,
		log,
		redisClient,
		rabbitClient,
	)

	r.Route("/", func(r chi.Router) {
		r.Get("/health", HealthH.Health)
	})

	r.Route("/v1/", func(r chi.Router) {
		r.Use(mdl.RequestAPIKeyAuth(log, authService))
		r.Get("/models", ModelsH.GetModels)
		r.Mount("/chat/", requestRouter)
	})

	r.Get("/swagger/*", httpSwagger.Handler(
		httpSwagger.URL(cfg.SwaggerURL),
	))

	return r
}
