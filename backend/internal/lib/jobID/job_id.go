package jobID

import (
	"crypto/rand"
	"encoding/hex"
)

func GenerateJobID() (string, error) {
	bytes := make([]byte, 12)

	if _, err := rand.Read(bytes); err != nil {
		return "", err
	}

	return hex.EncodeToString(bytes), nil
}
