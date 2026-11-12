package models

type Status string

const (
	StatusPending    Status = "pending"
	StatusProcessing Status = "processing"
	StatusDone       Status = "done"
	StatusFailed     Status = "failed"
)

type Request struct {
	BaseModel

	JobID  string `gorm:"uniqueIndex;not null;size:36"`
	Status Status `gorm:"type:varchar(20);not null;default:pending"`
	Prompt string `gorm:"type:text;not null"`
	Result string `gorm:"type:text"`

	OwnerID uint   `gorm:"not null;index"`
	Owner   APIKey `gorm:"constraint:OnUpdate:CASCADE,OnDelete:CASCADE"`
}
