version: '3.8'

services:
  chat-server:
    build:
      context: .
      dockerfile: Dockerfile.server
    container_name: chat-server
    ports:
      - "12345:12345"
    volumes:
      - chat-data:/app/data
    networks:
      - chat-network
    restart: unless-stopped
    environment:
      - JAVA_OPTS=-Xmx256m -Xms128m
    healthcheck:
      test: ["CMD", "netstat", "-tln", "|", "grep", ":12345"]
      interval: 30s
      timeout: 10s
      retries: 3

  chat-client:
    build:
      context: .
      dockerfile: Dockerfile.client
    networks:
      - chat-network
    environment:
      - DISPLAY=:99
    depends_on:
      - chat-server
    profiles:
      - client

volumes:
  chat-data:
    driver: local

networks:
  chat-network:
    driver: bridge
