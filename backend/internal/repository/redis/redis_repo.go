package redis

import (
	"context"
	"fmt"
	"time"

	"api/localai/internal/repository"

	"github.com/redis/go-redis/v9"
)

type redisRepository struct {
	rclient *redis.Client
}

func InitRedisRepo(rclient *redis.Client) repository.RedisRepository {
	return &redisRepository{
		rclient: rclient,
	}
}

func (r *redisRepository) Checkratelimit(ctx context.Context, apiKey string, limit int) error {
	redisKey := fmt.Sprintf("ratelimit:%s:%d", apiKey, time.Now().Unix()/60)

	count, _ := r.rclient.Incr(ctx, redisKey).Result()
	r.rclient.Expire(ctx, redisKey, 2*time.Minute)

	if int(count) > limit {
		return repository.ErrRateLimit
	}

	return nil
}

func (r *redisRepository) ReadResultStream(
	ctx context.Context,
	jobID string,
	lastID string,
) ([]redis.XMessage, error) {
	entries, err := r.rclient.XRead(ctx, &redis.XReadArgs{
		Streams: []string{
			"stream:job:" + jobID,
			lastID,
		},
		Block: 5 * time.Second,
		Count: 1,
	}).Result()
	if err != nil {
		return nil, err
	}

	return entries[0].Messages, nil
}

func (r *redisRepository) ReadResult(
	ctx context.Context,
	jobID string,
) ([]redis.XMessage, error) {
	entries, err := r.rclient.XRange(
		ctx,
		"stream:job:"+jobID,
		"-",
		"+",
	).Result()

	return entries, err
}

func (r *redisRepository) AppendChunk(ctx context.Context, jobID string, line string) error {
	return r.rclient.XAdd(ctx, &redis.XAddArgs{
		Stream: "stream:job:" + jobID,
		ID:     "*",
		Values: map[string]any{
			"token": line,
		},
	}).Err()
}
