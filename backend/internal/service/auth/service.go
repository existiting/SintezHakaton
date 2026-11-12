package auth

import (
	"context"

	"api/localai/internal/domains/models"
	"api/localai/internal/repository"
	"api/localai/internal/service"
)

type authService struct {
	repo repository.AuthRepository
}

func Init(repo repository.AuthRepository) service.AuthService {
	return &authService{
		repo: repo,
	}
}

func (s *authService) VerifyAPIKey(key string, ctx context.Context) (*models.APIKey, error) {
	const op = "internal.service.auth.VerifyAPIKey"

	dbKey, err := s.repo.GetAPIKeyByKey(key, ctx)
	if err != nil {
		return nil, err
	}

	return dbKey, nil
}
