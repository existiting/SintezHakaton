package request

import (
	"context"
	"fmt"

	ctxKeys "api/localai/internal/context"

	"api/localai/internal/domains"
	"api/localai/internal/domains/models"
	"api/localai/internal/lib/jobID"
	"api/localai/internal/repository"
	"api/localai/internal/service"
)

type requestService struct {
	repo       repository.RequestRepository
	redisRepo  repository.RedisRepository
	rabbitRepo repository.RabbitRepository
}

func Init(
	repo repository.RequestRepository,
	redisRepo repository.RedisRepository,
	rabbitRepo repository.RabbitRepository,
) service.RequestService {
	return &requestService{
		repo:       repo,
		redisRepo:  redisRepo,
		rabbitRepo: rabbitRepo,
	}
}

func (s *requestService) Create(request domains.AIRequestCredentials, ctx context.Context) (*models.Request, error) {
	const op = "internal.service.request.service.Create"

	apiKey, ok := ctx.Value(ctxKeys.ApiKeyKey).(string)
	if !ok {
		return nil, fmt.Errorf("%s: %s", op, "failed to get apiKey from context")
	}

	if err := s.redisRepo.Checkratelimit(ctx, apiKey, 3); err != nil {
		return nil, err
	}

	jobID, err := jobID.GenerateJobID()
	if err != nil {
		return nil, fmt.Errorf("%s: %w", op, err)
	}

	dbRequest, err := s.repo.Create(
		request.Prompt,
		jobID,
		ctx,
	)
	if err != nil {
		return nil, err
	}

	rabbitRequest := &domains.RabbitMQRequest{
		Prompt: request.Prompt,
		JobID:  jobID,
	}

	err = s.rabbitRepo.CreateRequest(ctx, rabbitRequest)
	if err != nil {
		s.repo.SetStatusByJobID(jobID, models.StatusFailed, ctx)

		return nil, err
	}

	return dbRequest, nil
}

func (s *requestService) GetStatusByJobID(jobID string, ctx context.Context) (string, error) {
	const op = "internal.service.request.service.GetStatusByJobID"

	dbRequest, err := s.repo.GetByJobID(
		jobID,
		ctx,
	)
	if err != nil {
		return "", err
	}

	return string(dbRequest.Status), nil
}

func (s *requestService) GetResultByJobID(jobID string, ctx context.Context) (string, error) {
	const op = "internal.service.request.service.GetResultByJobID"

	dbRequest, err := s.repo.GetByJobID(
		jobID,
		ctx,
	)
	if err != nil {
		return "", err
	}

	resultMessage, err1 := s.redisRepo.ReadResult(ctx, dbRequest.JobID)
	if err1 != nil {
		return "", err1
	}

	result := ""

	for _, message := range resultMessage {
		rawToken, ok := message.Values["token"]
		if !ok || rawToken == nil {
			fmt.Print("failed token")
			continue
		}

		token, ok := rawToken.(string)
		if !ok {
			continue
		}

		result = result + token
	}

	return result, nil
}
