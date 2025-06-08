#!/bin/bash

# Simple test script for Chat App Docker
echo "===== Testing Chat App Docker ====="

# Variables
IMAGE_NAME="chatapp"
CONTAINER_NAME="chatapp-test"
PORT="12345"

# Test counters
PASSED=0
FAILED=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo ""
    echo "Testing: $test_name"
    echo "----------------------------------------"
    
    if eval "$test_command"; then
        echo "✓ PASS: $test_name"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo "✗ FAIL: $test_name"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# Test 1: Check if Docker is installed
test_docker_installed() {
    docker --version > /dev/null 2>&1
}

# Test 2: Check if Java files exist
test_java_files_exist() {
    [ -f "ChatServer.java" ] && [ -f "ChatClient.java" ] && [ -f "ChatProtocol.java" ]
}

# Test 3: Check if Java files compile
test_java_compilation() {
    javac *.java > /dev/null 2>&1
}

# Test 4: Check if Dockerfile exists
test_dockerfile_exists() {
    [ -f "Dockerfile" ]
}

# Test 5: Build Docker image
test_docker_build() {
    docker build -t $IMAGE_NAME . > /dev/null 2>&1
}

# Test 6: Check if image was created
test_image_exists() {
    docker images | grep -q $IMAGE_NAME
}

# Test 7: Run container
test_container_run() {
    # Clean up first
    docker stop $CONTAINER_NAME > /dev/null 2>&1 || true
    docker rm $CONTAINER_NAME > /dev/null 2>&1 || true
    
    # Create data directory
    mkdir -p data
    
    # Run container
    docker run -d --name $CONTAINER_NAME -p $PORT:$PORT -v $(pwd)/data:/app/data $IMAGE_NAME > /dev/null 2>&1
}

# Test 8: Check if container is running
test_container_running() {
    sleep 3  # Give container time to start
    docker ps | grep -q $CONTAINER_NAME
}

# Test 9: Check if port is accessible
test_port_accessible() {
    sleep 2  # Give server time to start
    timeout 5 bash -c "</dev/tcp/localhost/$PORT" > /dev/null 2>&1
}

# Test 10: Check data directory
test_data_directory() {
    [ -d "data" ]
}

# Cleanup function
cleanup() {
    echo ""
    echo "Cleaning up test resources..."
    docker stop $CONTAINER_NAME > /dev/null 2>&1 || true
    docker rm $CONTAINER_NAME > /dev/null 2>&1 || true
}

# Main test execution
echo "Starting validation tests..."

# Run all tests
run_test "Docker Installation" "test_docker_installed"
run_test "Java Files Exist" "test_java_files_exist"
run_test "Java Compilation" "test_java_compilation"
run_test "Dockerfile Exists" "test_dockerfile_exists"
run_test "Docker Image Build" "test_docker_build"
run_test "Docker Image Created" "test_image_exists"
run_test "Container Startup" "test_container_run"
run_test "Container Running" "test_container_running"
run_test "Port Accessibility" "test_port_accessible"
run_test "Data Directory" "test_data_directory"

# Cleanup
cleanup

# Final results
echo ""
echo "========================================="
echo "           TEST RESULTS"
echo "========================================="
echo "Tests Passed: $PASSED"
echo "Tests Failed: $FAILED"
echo "Total Tests:  $((PASSED + FAILED))"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo "🎉 ALL TESTS PASSED!"
    echo "Your Docker setup is working correctly."
    exit 0
else
    echo ""
    echo "❌ SOME TESTS FAILED"
    echo "Please check the failed tests above."
    exit 1
fi
