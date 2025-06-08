#!/bin/bash

# Deployment script for Chat Application
echo "=== Chat Application Deployment Script ==="

# Colors for display
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display messages
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_cmd() {
    echo -e "${BLUE}[CMD]${NC} $1"
}

# Function to display help
show_help() {
    echo "Usage: $0 [OPTION]"
    echo "Options:"
    echo "  start-server    Start the chat server"
    echo "  start-client    Start a chat client"
    echo "  stop           Stop all containers"
    echo "  status         Show container status"
    echo "  logs-server    Show server logs"
    echo "  logs-client    Show client logs"
    echo "  cleanup        Clean up containers and volumes"
    echo "  help           Show this help"
}

# Function to start the server
start_server() {
    log_info "Starting chat server..."
    
    # Create volume for user data
    docker volume create chat-data 2>/dev/null || true
    
    # Start the server
    log_cmd "docker run -d --name chat-server --network chat-network -p 12345:12345 -v chat-data:/app/data chat-server:latest"
    
    if docker run -d \
        --name chat-server \
        --network chat-network \
        -p 12345:12345 \
        -v chat-data:/app/data \
        --restart unless-stopped \
        chat-server:latest; then
        log_info "Server started successfully"
        log_info "Port: 12345"
        log_info "Network: chat-network"
    else
        log_error "Error starting server"
        return 1
    fi
}

# Function to start a client
start_client() {
    CLIENT_NAME="chat-client-$(date +%s)"
    log_info "Starting chat client ($CLIENT_NAME)..."
    
    log_cmd "docker run -d --name $CLIENT_NAME --network chat-network -e DISPLAY=:99 chat-client:latest"
    
    if docker run -d \
        --name $CLIENT_NAME \
        --network chat-network \
        -e DISPLAY=:99 \
        --restart unless-stopped \
        chat-client:latest; then
        log_info "Client started successfully"
        log_info "Client name: $CLIENT_NAME"
    else
        log_error "Error starting client"
        return 1
    fi
}

# Function to stop all containers
stop_containers() {
    log_info "Stopping all chat containers..."
    
    # Stop server
    if docker ps -q --filter "name=chat-server" | grep -q .; then
        docker stop chat-server
        docker rm chat-server
        log_info "Server stopped"
    fi
    
    # Stop all clients
    for client in $(docker ps -q --filter "name=chat-client-*"); do
        CLIENT_NAME=$(docker inspect --format='{{.Name}}' $client | sed 's/\///')
        docker stop $client
        docker rm $client
        log_info "Client $CLIENT_NAME stopped"
    done
}

# Function to show status
show_status() {
    log_info "Container status:"
    docker ps --filter "name=chat-server" --filter "name=chat-client-*" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
}

# Function to show server logs
show_server_logs() {
    log_info "Server logs:"
    docker logs -f chat-server
}

# Function to show client logs
show_client_logs() {
    log_info "Available clients:"
    docker ps --filter "name=chat-client-*" --format "{{.Names}}"
    echo
    read -p "Enter client name to view logs: " CLIENT_NAME
    docker logs -f $CLIENT_NAME
}

# Function to cleanup
cleanup() {
    log_warn "This will remove all chat containers and data. Are you sure? (y/N)"
    read -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        stop_containers
        docker volume rm chat-data 2>/dev/null || true
        docker network rm chat-network 2>/dev/null || true
        log_info "Cleanup completed"
    else
        log_info "Cleanup cancelled"
    fi
}

# Main script logic
case "$1" in
    start-server)
        start_server
        ;;
    start-client)
        start_client
        ;;
    stop)
        stop_containers
        ;;
    status)
        show_status
        ;;
    logs-server)
        show_server_logs
        ;;
    logs-client)
        show_client_logs
        ;;
    cleanup)
        cleanup
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        show_help
        exit 1
        ;;
esac
