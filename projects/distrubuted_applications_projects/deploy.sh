#!/bin/bash

# Deployment script for Chat Application with X11 forwarding
echo "=== Chat Application Deployment Script (X11 Forwarding) ==="

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

# Function to check X11 availability
check_x11() {
    if [ -z "$DISPLAY" ]; then
        log_error "DISPLAY environment variable is not set"
        log_info "Make sure you're running this in a graphical environment"
        return 1
    fi
    
    if ! xhost &>/dev/null; then
        log_error "xhost command not found. Please install X11 utilities:"
        log_info "sudo apt-get install x11-xserver-utils"
        return 1
    fi
    
    return 0
}

# Function to setup X11 permissions
setup_x11() {
    log_info "Setting up X11 permissions..."
    
    # Allow connections from docker containers
    xhost +local:docker >/dev/null 2>&1
    
    # Get the X11 socket path
    X11_SOCKET="/tmp/.X11-unix"
    
    if [ ! -d "$X11_SOCKET" ]; then
        log_error "X11 socket directory not found: $X11_SOCKET"
        return 1
    fi
    
    log_info "X11 display: $DISPLAY"
    log_info "X11 socket: $X11_SOCKET"
    return 0
}

# Function to display help
show_help() {
    echo "Usage: $0 [OPTION]"
    echo "Options:"
    echo "  start-server    Start the chat server with GUI"
    echo "  start-client    Start a chat client with GUI"
    echo "  stop           Stop all containers"
    echo "  status         Show container status"
    echo "  logs-server    Show server logs"
    echo "  logs-client    Show client logs"
    echo "  cleanup        Clean up containers and volumes"
    echo "  test-x11       Test X11 forwarding setup"
    echo "  help           Show this help"
    echo ""
    echo "Requirements:"
    echo "  - X11 server running (graphical desktop environment)"
    echo "  - xhost utility installed (sudo apt-get install x11-xserver-utils)"
}

# Function to test X11 setup
test_x11() {
    log_info "Testing X11 forwarding setup..."
    
    if ! check_x11; then
        return 1
    fi
    
    if ! setup_x11; then
        return 1
    fi
    
    log_info "Running X11 test container..."
    log_cmd "docker run --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix openjdk:11-jre-slim java -version"
    
    if docker run --rm \
        -e DISPLAY=$DISPLAY \
        -v /tmp/.X11-unix:/tmp/.X11-unix \
        openjdk:11-jre-slim \
        java -version; then
        log_info "X11 forwarding test successful!"
        return 0
    else
        log_error "X11 forwarding test failed"
        return 1
    fi
}

# Function to start the server
start_server() {
    log_info "Starting chat server with GUI..."
    
    # Check X11 availability
    if ! check_x11; then
        return 1
    fi
    
    if ! setup_x11; then
        return 1
    fi
    
    # Create volume for user data
    docker volume create chat-data 2>/dev/null || true
    
    # Start the server with X11 forwarding
    log_cmd "docker run -d --name chat-server --network chat-network -p 12345:12345 -v chat-data:/app/data -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix chat-server:latest"
    
    if docker run -d \
        --name chat-server \
        --network chat-network \
        -p 12345:12345 \
        -v chat-data:/app/data \
        -e DISPLAY=$DISPLAY \
        -v /tmp/.X11-unix:/tmp/.X11-unix \
        --restart unless-stopped \
        chat-server:latest; then
        log_info "Server started successfully with GUI"
        log_info "Port: 12345"
        log_info "Network: chat-network"
        log_info "GUI should appear on your desktop"
    else
        log_error "Error starting server"
        return 1
    fi
}

# Function to start a client
start_client() {
    CLIENT_NAME="chat-client-$(date +%s)"
    log_info "Starting chat client ($CLIENT_NAME) with GUI..."
    
    # Check X11 availability
    if ! check_x11; then
        return 1
    fi
    
    if ! setup_x11; then
        return 1
    fi
    
    log_cmd "docker run -d --name $CLIENT_NAME --network chat-network -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix chat-client:latest"
    
    if docker run -d \
        --name $CLIENT_NAME \
        --network chat-network \
        -e DISPLAY=$DISPLAY \
        -v /tmp/.X11-unix:/tmp/.X11-unix \
        --restart unless-stopped \
        chat-client:latest; then
        log_info "Client started successfully with GUI"
        log_info "Client name: $CLIENT_NAME"
        log_info "GUI should appear on your desktop"
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
    
    # Reset X11 permissions
    xhost -local:docker >/dev/null 2>&1
    log_info "X11 permissions reset"
}

# Function to show status
show_status() {
    log_info "Container status:"
    docker ps --filter "name=chat-server" --filter "name=chat-client-*" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo
    log_info "X11 Display: ${DISPLAY:-Not Set}"
    log_info "X11 Socket: $(ls -la /tmp/.X11-unix 2>/dev/null | wc -l) sockets"
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
    test-x11)
        test_x11
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
