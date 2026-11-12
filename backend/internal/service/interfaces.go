package service

import (
	"context"

	"api/localai/internal/domains"
	"api/localai/internal/domains/models"
)

type AuthService interface {
	VerifyAPIKey(key string, ctx context.Context) (*models.APIKey, error)
}

type RequestService interface {
	Create(request domains.AIRequestCredentials, ctx context.Context) (*models.Request, error)
	GetStatusByJobID(jobID string, ctx context.Context) (string, error)
	GetResultByJobID(jobID string, ctx context.Context) (string, error)
}
