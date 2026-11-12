package domains

type AIRequestCredentials struct {
	Prompt string
}

type RabbitMQRequest struct {
	Prompt string `json:"prompt"`
	JobID  string `json:"jobID"`
}
