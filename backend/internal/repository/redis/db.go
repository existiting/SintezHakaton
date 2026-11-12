package redis

import (
	"context"
	"fmt"

	"github.com/caarlos0/env/v11"
	"github.com/redis/go-redis/v9"
)

type configRedis struct {
	Addr        string `env:"REDIS_ADDR,required"`
	Password    string `env:"REDIS_USER_PASSWORD,required"`
	DB          int    `env:"REDIS_DB,required"`
	User        string `env:"REDIS_USER,required"`
	MaxRetries  int    `env:"REDIS_MAXRETRIES,required"`
	DialTimeout string `env:"REDIS_DIALTIMEOUT,required"`
	TimeOut     string `env:"REDIS_TIMEOUT"`
}

func NewClient() (*redis.Client, error) {
	const op = "internal.repository.redis.NewClient"

	cfg, err := LoadConfig()
	if err != nil {
		return nil, fmt.Errorf("failed to connect to redis server: %w\n", err.Error())
	}

	db := redis.NewClient(&redis.Options{
		Addr:       cfg.Addr,
		Password:   cfg.Password,
		DB:         cfg.DB,
		Username:   cfg.User,
		MaxRetries: cfg.MaxRetries,
	})

	ctx := context.Background()
	if err := db.Ping(ctx).Err(); err != nil {
		fmt.Printf("failed to connect to redis server: %s\n", err.Error())
		return nil, err
	}

	return db, nil
}

func LoadConfig() (*configRedis, error) {
	config := &configRedis{}
	if err := env.Parse(config); err != nil {
		return nil, fmt.Errorf("invalid config: %w", err)
	}
	return config, nil
}
