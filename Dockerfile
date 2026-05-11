# STAGE 1: Build the Go binary
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY go.mod ./
RUN go mod download
COPY . .
RUN go build -o hive main.go

# STAGE 2: Final lightweight runner
FROM alpine:latest
ENV ENVIRONMENT=production
WORKDIR /app
RUN apk add --no-cache curl
COPY --from=builder /app/hive .
COPY --from=builder /app/media ./media
RUN mkdir -p logs
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
CMD ["./hive"]