package rabbitmq

import (
	"fmt"

	"github.com/caarlos0/env/v11"
	amqp "github.com/rabbitmq/amqp091-go"
)

type configRedis struct {
	Addr     string `env:"RABBITMQ_ADDR,required"`
	Password string `env:"RABBITMQ_PASS,required"`
	User     string `env:"RABBITMQ_USER,required"`
}

type RabbitClient struct {
	Client  *amqp.Connection
	Channel *amqp.Channel
}

func (rabClient *RabbitClient) InitQueues(channel *amqp.Channel) error {
	_, err := channel.QueueDeclare(
		RequestQueue, // name
		false,        // durable
		false,        // delete when unused
		false,        // exclusive
		false,        // no-wait
		nil,          // arguments
	)
	if err != nil {
		return fmt.Errorf("failed to declare a queue. Error: %s", err)
	}

	return nil
}

func NewClient() (*RabbitClient, error) {
	const op = "internal.repository.redis.NewClient"

	cfg, err := LoadConfig()
	if err != nil {
		return nil, fmt.Errorf("failed to connect to rabbitmq server: %w", err)
	}

	url := fmt.Sprintf(
		"amqp://%s:%s@%s/",
		cfg.User,
		cfg.Password,
		cfg.Addr,
	)

	client, err := amqp.Dial(url)
	if err != nil {
		defer func() {
			_ = client.Close()
		}()

		return nil, fmt.Errorf("failed to connect to rabbitmq server: %w", err)
	}

	ch, err := client.Channel()
	if err != nil {
		defer func() {
			_ = ch.Close()
		}()

		return nil, err
	}

	db := RabbitClient{
		Client:  client,
		Channel: ch,
	}

	return &db, nil
}

func LoadConfig() (*configRedis, error) {
	config := &configRedis{}
	if err := env.Parse(config); err != nil {
		return nil, fmt.Errorf("invalid config: %w", err)
	}
	return config, nil
}
