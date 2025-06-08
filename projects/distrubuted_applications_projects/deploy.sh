#!/bin/bash

# Simple deployment script for Chat App
CONTAINER_NAME="chatapp-server"
IMAGE_NAME="chatapp"
PORT="12345"

# Function to print messages
print_message() {
    echo "[INFO] $1"
}

# Function to start the application
start_app() {
    print_message "Starting Chat Application..."
    
    # Create data directory
    mkdir -p data
    
    # Stop existing container
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
    
    # Start new container
    docker run -d \
        --name $CONTAINER_NAME \
        -p $PORT:$PORT \
        -v $(pwd)/data:/app/data \
        $IMAGE_NAME
    
    if [ $? -eq 0 ]; then
        print_message "Application started successfully!"
        print_message "Access the server at localhost:$PORT"
    else
        echo "[ERROR] Failed to start application"
        exit 1
    fi
}

# Function to stop the application
stop_app() {
    print_message "Stopping Chat Application..."
    docker stop $CONTAINER_NAME
    print_message "Application stopped"
}

# Function to show application status
show_status() {
    print_message "Application Status:"
    if docker ps | grep -q $CONTAINER_NAME; then
        echo "✓ Application is running"
        docker ps --filter "name=$CONTAINER_NAME"
    else
        echo "✗ Application is not running"
    fi
}

# Function to show logs
show_logs() {
    print_message "Showing application logs..."
    docker logs -f $CONTAINER_NAME
}

# Function to restart the application
restart_app() {
    print_message "Restarting Chat Application..."
    stop_app
    sleep 2
    start_app
}

# Main script logic
case "$1" in
    "start")
        start_app
        ;;
    "stop")
        stop_app
        ;;
    "restart")
        restart_app
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the chat application"
        echo "  stop    - Stop the chat application"
        echo "  restart - Restart the chat application"
        echo "  status  - Show application status"
        echo "  logs    - Show application logs"
        exit 1
        ;;
esac
