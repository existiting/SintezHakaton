package worker

import (
	"context"
	"encoding/json"
	"fmt"
	"log/slog"

	"api/localai/internal/domains"
	"api/localai/internal/domains/models"
	"api/localai/internal/lib/logger/sl"
	"api/localai/internal/lib/runner"
	"api/localai/internal/repository"

	"github.com/rabbitmq/amqp091-go"
)

type workerService struct {
	log        *slog.Logger
	repo       repository.RequestRepository
	redisRepo  repository.RedisRepository
	rabbitRepo repository.RabbitRepository
	Runner     runner.Runner
}

func Init(
	log *slog.Logger,
	repo repository.RequestRepository,
	redisRepo repository.RedisRepository,
	rabbitRepo repository.RabbitRepository,
	Runner runner.Runner,
) *workerService {
	return &workerService{
		log:        log,
		repo:       repo,
		redisRepo:  redisRepo,
		rabbitRepo: rabbitRepo,
		Runner:     Runner,
	}
}

func (s *workerService) Run(ctx context.Context) error {
	const op = "internal.service.worker.Run"

	log := s.log.With("op", op)

	msgs, err := s.rabbitRepo.ConsumeRequest(ctx)
	if err != nil {
		return fmt.Errorf("%s: consume: %w", op, err)
	}

	for {
		select {
		case <-ctx.Done():
			log.Info("worker stopped")

			return nil

		case msg, ok := <-msgs:
			if !ok {
				return fmt.Errorf("%s: messages channel closed", op)
			}
			if err := s.HandleMessage(ctx, msg); err != nil {
				log.Error(
					"handle message failed",
					sl.Err(err),
					slog.String("body", string(msg.Body)),
				)

				msg.Nack(false, false)

				continue
			}
			msg.Ack(false)
		}
	}
}

func (s *workerService) HandleMessage(ctx context.Context, msg amqp091.Delivery) error {
	const op = "internal.service.worker.handleMessage"

	var payload domains.RabbitMQRequest

	if err := json.Unmarshal(msg.Body, &payload); err != nil {
		return fmt.Errorf("%s: unmarshal: %w", op, err)
	}
	s.log.Info("jobID", slog.String("jobID", payload.JobID))

	log := s.log.With(slog.String("jobID", payload.JobID))

	req, err := s.repo.GetByJobID(payload.JobID, ctx)
	if err != nil {
		return fmt.Errorf("%s: get request: %w", op, err)
	}
	s.log.Info("jobID", slog.String("jobID", req.JobID))

	if err = s.repo.SetStatusByJobID(payload.JobID, "processing", ctx); err != nil {
		return fmt.Errorf("%s: update status request: %w", op, err)
	}

	log.Info("processing request")

	err = s.Runner.Run(ctx, runner.Params{
		RequestID: req.JobID,
		Prompt:    payload.Prompt,
	})
	if err != nil {
		_ = s.repo.SetStatusByJobID(payload.JobID, models.StatusFailed, ctx)

		return fmt.Errorf("%s: runner: %w", op, err)
	}

	if err := s.repo.SetStatusByJobID(payload.JobID, models.StatusDone, ctx); err != nil {
		return fmt.Errorf("%s: update status done: %w", op, err)
	}

	log.Info("request processed successfully")

	return nil
}
