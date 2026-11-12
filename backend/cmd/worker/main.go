package main

import (
	"context"
	"log/slog"
	"os"
	"os/signal"
	"syscall"

	"api/localai/internal/config"
	"api/localai/internal/lib/logger"
	"api/localai/internal/lib/logger/sl"
	"api/localai/internal/lib/runner"
	"api/localai/internal/repository/postgres"
	"api/localai/internal/repository/rabbitmq"
	"api/localai/internal/repository/redis"
	workerSvc "api/localai/internal/service/worker"
)

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
	repo := postgres.InitRequestRepository(db)

	log.Info("init redis client..")
	redisClient, err := redis.NewClient()
	if err != nil {
		log.Error("failed to init redis client", sl.Err(err))

		os.Exit(1)
	}
	redisRepo := redis.InitRedisRepo(redisClient)

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
	rabbitRepo := rabbitmq.InitRabbitRepo(rabbitClient)

	log.Info("init runner..")
	runner := runner.New(
		cfg.Runner.PythonBinPath,
		cfg.Runner.PythonScriptPath,
		redisRepo,
	)

	svc := workerSvc.Init(
		log,
		repo,
		redisRepo,
		rabbitRepo,
		runner,
	)

	ctx, stop := signal.NotifyContext(
		context.Background(),
		os.Interrupt, syscall.SIGTERM,
	)
	defer stop()

	if err := svc.Run(ctx); err != nil {
		log.Error("worker exited with error", slog.String("err", err.Error()))
	}
}
