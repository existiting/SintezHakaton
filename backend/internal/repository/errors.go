package repository

import "errors"

var (
	ErrNotFound  = errors.New("not found")
	ErrNotExists = errors.New("not exists")
	ErrUniqueKey = errors.New("object already exist")
	ErrRateLimit = errors.New("rate limits to high")
)
