FROM golang:1.26-alpine AS builder

WORKDIR /app

COPY go.mod ./
RUN go mod download

COPY . .

RUN go build -o sentry ./cmd/sentry

FROM alpine:3.19

WORKDIR /app

COPY --from=builder /app/sentry .

USER 1001

CMD ["./sentry"]
