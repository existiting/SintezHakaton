package middleware

import (
	"context"
	"errors"
	"log/slog"
	"net/http"

	ctxKeys "api/localai/internal/context"
	"api/localai/internal/lib/api/response"
	"api/localai/internal/lib/logger/sl"
	"api/localai/internal/repository"
	"api/localai/internal/service"
)

func RequestAPIKeyAuth(log *slog.Logger, authService service.AuthService) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		log = log.With(
			slog.String("component", "middleware/auth"),
		)

		fn := func(w http.ResponseWriter, r *http.Request) {
			apiKey := r.Header.Get("Authorization")
			if apiKey == "" {
				const msg = "failed to get Authorization key from Headers"

				log.Error(msg)

				response.ResponseError(w, r, 401, msg)

				return
			}

			dbKey, err := authService.VerifyAPIKey(apiKey, r.Context())
			if err != nil {
				if errors.Is(err, repository.ErrNotFound) {
					const msg = "Incorrect authorization api key"

					log.Error(msg, sl.Err(err))

					response.ResponseError(w, r, 401, msg)

					return
				}

				const msg = "internal server error"

				log.Error(msg, sl.Err(err))

				response.ResponseError(w, r, 500, msg)

				return
			}

			newCtx := context.WithValue(r.Context(), ctxKeys.ApiKeyID, dbKey.ID)
			newCtx = context.WithValue(newCtx, ctxKeys.ApiKeyKey, dbKey.Key)
			newReq := r.WithContext(newCtx)

			next.ServeHTTP(w, newReq)
		}

		return http.HandlerFunc(fn)
	}
}
