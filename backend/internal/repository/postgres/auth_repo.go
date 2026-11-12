package postgres

import (
	"context"
	"errors"
	"fmt"

	"api/localai/internal/domains/models"
	"api/localai/internal/repository"

	"gorm.io/gorm"
)

type authRepository struct {
	db *Database
}

func Init(db *Database) repository.AuthRepository {
	return &authRepository{
		db: db,
	}
}

func (repo *authRepository) GetAPIKeyByKey(key string, ctx context.Context) (*models.APIKey, error) {
	const op = "internal.repository.postgres.auth.GetAPIKeyByKey"

	dbKey := models.APIKey{}

	res := repo.db.db.WithContext(ctx).Where("key = ?", key).First(&dbKey)
	if res.Error != nil {
		if errors.Is(res.Error, gorm.ErrRecordNotFound) {
			return nil, repository.ErrNotFound
		}

		return nil, fmt.Errorf("%s: %w", op, res.Error)
	}

	return &dbKey, nil
}
