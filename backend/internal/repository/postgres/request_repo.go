package postgres

import (
	"context"
	"errors"
	"fmt"

	ctxKeys "api/localai/internal/context"
	"api/localai/internal/domains/models"
	"api/localai/internal/repository"

	"gorm.io/gorm"
)

type requestRepository struct {
	db *Database
}

func InitRequestRepository(db *Database) repository.RequestRepository {
	return &requestRepository{
		db: db,
	}
}

func (repo *requestRepository) Create(
	prompt string,
	jobID string,
	ctx context.Context,
) (*models.Request, error) {
	const op = "internal.repository.postgres.request_repo.Create"

	ownerID := ctx.Value(ctxKeys.ApiKeyID).(uint)

	dbRequest := models.Request{
		JobID:   jobID,
		Status:  models.StatusPending,
		Prompt:  prompt,
		Result:  "",
		OwnerID: ownerID,
	}

	res := repo.db.db.WithContext(ctx).Create(&dbRequest)
	if res.Error != nil {
		if errors.Is(res.Error, gorm.ErrDuplicatedKey) {
			return nil, repository.ErrUniqueKey
		}

		return nil, fmt.Errorf("%s: %w", op, res.Error)
	}

	return &dbRequest, nil
}

func (repo *requestRepository) GetByJobID(
	jobID string,
	ctx context.Context,
) (*models.Request, error) {
	const op = "repository.postgres.request_repo.GetByJobID"

	dbRequest := models.Request{}

	res := repo.db.db.WithContext(ctx).Where("job_id = ?", jobID).First(&dbRequest)
	if res.Error != nil {
		if errors.Is(res.Error, gorm.ErrRecordNotFound) {
			return nil, repository.ErrNotFound
		}

		return nil, fmt.Errorf("%s: %w", op, res.Error)
	}

	return &dbRequest, nil
}

func (repo *requestRepository) SetStatusByJobID(
	jobID string,
	status models.Status,
	ctx context.Context,
) error {
	const op = "repository.postgres.request_repo.SetStatusByJobID"

	res := repo.db.db.WithContext(ctx).
		Model(&models.Request{}).
		Where("job_id = ?", jobID).
		Update("status", status)
	if res.Error != nil {
		return fmt.Errorf("%s: %w", op, res.Error)
	}

	if res.RowsAffected == 0 {
		return repository.ErrNotFound
	}

	return nil
}

func (repo *requestRepository) SetResultByJobID(
	jobID string,
	result string,
	ctx context.Context,
) error {
	const op = "repository.postgres.request_repo.SetResultByJobID"

	res := repo.db.db.WithContext(ctx).
		Model(&models.Request{}).
		Where("job_id = ?").
		Update("result", result)
	if res.Error != nil {
		return fmt.Errorf("%s: %w", op, res.Error)
	}
	if res.RowsAffected == 0 {
		return repository.ErrNotFound
	}

	return nil
}
