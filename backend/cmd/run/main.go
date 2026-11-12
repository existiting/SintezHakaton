package main

import (
	"log/slog"
	"net/http"
	"os"

	"api/localai/internal/config"
	"api/localai/internal/handlers"
	"api/localai/internal/lib/logger"
	"api/localai/internal/lib/logger/sl"
	"api/localai/internal/repository/postgres"
	"api/localai/internal/repository/rabbitmq"
	"api/localai/internal/repository/redis"
)

// @title           Local AI API
// @version         1.0
// @description     API for local ai runners
// @host            localhost:8080
// @BasePath        /
func main() {
	cfg := config.MustInit()

	log := logger.SetupLogger(cfg.Env)
	log.Info("starting app...", slog.String("env", cfg.Env))

	log.Info("init storage...")
	db, err := postgres.New()
	if err != nil {
		log.Error("failed to init storage", sl.Err(err))

		os.Exit(1)
	}

	log.Info("init redis client..")
	redisClient, err := redis.NewClient()
	if err != nil {
		log.Error("failed to init redis client", sl.Err(err))

		os.Exit(1)
	}

	log.Info("init rabbimq client..")
	rabbitClient, err := rabbitmq.NewClient()
	if err != nil {
		log.Error("failed to init rabbit client", sl.Err(err))

		os.Exit(1)
	}

	log.Info("init rammitmq queue..")
	if err := rabbitClient.InitQueues(rabbitClient.Channel); err != nil {
		log.Error("failed to init rabbitmq queues", sl.Err(err))
	}

	router := handlers.Init(
		log,
		db,
		redisClient,
		rabbitClient,
		cfg,
	)

	log.Info("Server is start", slog.String("address", cfg.Address))
	http.ListenAndServe(cfg.Address, router)
}
