package response

import (
	"net/http"

	"github.com/go-chi/render"
)

type Response struct {
	Detail     string `json:"detail,omitempty"`
	StatusCode int    `json:"status_code,omitempty"`
}

func OK() Response {
	return Response{
		StatusCode: 200,
	}
}

func Error(msg string, code int) Response {
	return Response{
		Detail:     msg,
		StatusCode: code,
	}
}

func ResponseError(w http.ResponseWriter, r *http.Request, statusCode int, msg string) {
	w.WriteHeader(statusCode)

	render.JSON(w, r, Error(msg, statusCode))
}
