#!/bin/bash

# Simple build script for Chat App Docker
echo "===== Building Chat App ====="

# Variables
IMAGE_NAME="chatapp"
CONTAINER_NAME="chatapp-server"
PORT="12345"

# Function to print messages
print_message() {
    echo "[INFO] $1"
}

# Step 1: Compile Java files
print_message "Compiling Java files..."
if [ ! -f "ChatServer.java" ]; then
    echo "[ERROR] ChatServer.java not found!"
    exit 1
fi

javac *.java
if [ $? -eq 0 ]; then
    print_message "Java compilation successful"
else
    echo "[ERROR] Java compilation failed"
    exit 1
fi

# Step 2: Build Docker image
print_message "Building Docker image..."
docker build -t $IMAGE_NAME .
if [ $? -eq 0 ]; then
    print_message "Docker image built successfully"
else
    echo "[ERROR] Docker build failed"
    exit 1
fi

# Step 3: Test the image
print_message "Testing Docker image..."
if docker images | grep -q $IMAGE_NAME; then
    print_message "Docker image test passed"
else
    echo "[ERROR] Docker image not found"
    exit 1
fi

# Step 4: Ask if user wants to run the application
read -p "Do you want to run the application now? (y/n): " choice
if [ "$choice" = "y" ] || [ "$choice" = "Y" ]; then
    # Stop existing container if running
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
    
    # Create data directory
    mkdir -p data
    
    # Run the container
    print_message "Starting application container..."
    docker run -d \
        --name $CONTAINER_NAME \
        -p $PORT:$PORT \
        -v $(pwd)/data:/app/data \
        $IMAGE_NAME
    
    if [ $? -eq 0 ]; then
        print_message "Application started successfully!"
        print_message "Server is running on port $PORT"
        print_message "Data will be saved in ./data directory"
        print_message ""
        print_message "To stop: docker stop $CONTAINER_NAME"
        print_message "To view logs: docker logs $CONTAINER_NAME"
    else
        echo "[ERROR] Failed to start application"
        exit 1
    fi
fi

print_message "Build process completed!"
