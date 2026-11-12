# ===== Build =====
FROM golang:1.27-alpine AS builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build \
    -ldflags="-s -w" \
    -o server \
    ./cmd/run

RUN CGO_ENABLED=0 GOOS=linux go build \
    -ldflags="-s -w" \
    -o worker \
    ./cmd/worker

# ===== Runtime =====
FROM alpine:3.22

WORKDIR /app

RUN apk --no-cache add ca-certificates

COPY --from=builder /app/server ./server
COPY --from=builder /app/worker ./worker


COPY --from=builder /app/config ./config

CMD ["./server"]
