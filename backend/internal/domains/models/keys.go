package models

import "time"

type APIKey struct {
	BaseModel

	Key       string    `gorm:"uniqueIndex;not null;size:64"`
	ExpiredAt time.Time `gorm:"not null;default:(CURRENT_TIMESTAMP + INTERVAL '30 days')"`

	Requests []Request `gorm:"foreignKey:OwnerID;constraint:OnDelete:CASCADE"`
}
