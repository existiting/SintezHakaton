package repository

import (
	"context"

	"api/localai/internal/domains"
	"api/localai/internal/domains/models"

	amqp "github.com/rabbitmq/amqp091-go"
	"github.com/redis/go-redis/v9"
)

type AuthRepository interface {
	GetAPIKeyByKey(key string, ctx context.Context) (*models.APIKey, error)
}

type RequestRepository interface {
	Create(
		prompt string,
		jobID string,
		ctx context.Context,
	) (*models.Request, error)

	GetByJobID(
		jobID string,
		ctx context.Context,
	) (*models.Request, error)

	SetStatusByJobID(
		jobID string,
		status models.Status,
		ctx context.Context,
	) error

	SetResultByJobID(
		jobID string,
		result string,
		ctx context.Context,
	) error
}

type RedisRepository interface {
	Checkratelimit(ctx context.Context, apiKey string, limit int) error
	ReadResultStream(ctx context.Context, jobID, lastID string) ([]redis.XMessage, error)
	ReadResult(ctx context.Context, jobID string) ([]redis.XMessage, error)
	AppendChunk(ctx context.Context, requestID string, line string) error
}

type RabbitRepository interface {
	CreateRequest(ctx context.Context, body *domains.RabbitMQRequest) error
	ConsumeRequest(ctx context.Context) (<-chan amqp.Delivery, error)
}
