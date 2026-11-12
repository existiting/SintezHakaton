package postgres

import (
	"fmt"
	"time"

	"api/localai/internal/domains/models"

	"github.com/caarlos0/env/v11"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

type Database struct {
	db *gorm.DB
}

type ConfigDB struct {
	Host     string `env:"POSTGRES_HOST,required"`
	User     string `env:"POSTGRES_USER,required"`
	Password string `env:"POSTGRES_PASSWORD,required"`
	DBName   string `env:"POSTGRES_DB,required"`
	Port     string `env:"POSTGRES_PORT,required"`
	Sllmode  string `env:"POSTGRES_SSLMODE"`
	TimeZone string `env:"POSTGRES_TIMEZONE"`
}

func New() (*Database, error) {
	const op = "repository.postress.db"

	config, err := LoadConfig()
	if err != nil {
		panic(err)
	}

	dsn := fmt.Sprintf(
		"host=%s user=%s password=%s dbname=%s port=%s sslmode=%s TimeZone=%s",
		config.Host,
		config.User,
		config.Password,
		config.DBName,
		config.Port,
		config.Sllmode,
		config.TimeZone,
	)

	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{
		TranslateError: true,
		NowFunc: func() time.Time {
			return time.Now().UTC()
		},
	})
	if err != nil {
		return nil, fmt.Errorf("%s: %w", op, err)
	}

	// TODO: add db models to migrate
	if err = db.AutoMigrate(&models.APIKey{}, &models.Request{}); err != nil {
		return nil, fmt.Errorf("%s: %w", op, err)
	}

	return &Database{
		db: db,
	}, nil
}

func LoadConfig() (*ConfigDB, error) {
	config := &ConfigDB{}
	if err := env.Parse(config); err != nil {
		return nil, fmt.Errorf("invalid config: %w", err)
	}
	return config, nil
}
