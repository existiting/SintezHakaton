package rabbitmq

import (
	"context"
	"encoding/json"

	"api/localai/internal/domains"
	"api/localai/internal/repository"

	amqp "github.com/rabbitmq/amqp091-go"
)

type rabbitRepository struct {
	client *RabbitClient
}

func InitRabbitRepo(client *RabbitClient) repository.RabbitRepository {
	return &rabbitRepository{
		client: client,
	}
}

func (repo *rabbitRepository) CreateRequest(ctx context.Context, body *domains.RabbitMQRequest) error {
	rbody, err := json.Marshal(body)
	if err != nil {
		return err
	}

	err = repo.client.Channel.PublishWithContext(
		ctx,
		"",
		RequestQueue,
		false,
		false, amqp.Publishing{
			ContentType: "application/json",
			Body:        rbody,
		},
	)
	if err != nil {
		return err
	}

	return nil
}

func (repo *rabbitRepository) ConsumeRequest(ctx context.Context) (<-chan amqp.Delivery, error) {
	msgs, err := repo.client.Channel.Consume(
		RequestQueue,
		"",
		false,
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		return nil, err
	}

	return msgs, nil
}
