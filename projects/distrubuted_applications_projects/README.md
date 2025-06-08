# Docker Chat Application Project

## Overview
This project containerizes a Java chat application using Docker. The application consists of a chat server and client that allows multiple users to communicate in real-time.

## Project Structure
```
chat-docker/
├── Dockerfile           # Docker image definition
├── docker-compose.yml   # Docker Compose configuration
├── build.sh            # Build script
├── deploy.sh           # Deployment script
├── ChatServer.java     # Chat server code
├── ChatClient.java     # Chat client code
├── ChatProtocol.java   # Protocol interface
└── data/               # Persistent data directory
```

## Quick Start

### Prerequisites
- Docker installed
- Java 11+ (for compilation)

### Build and Run
1. **Make scripts executable:**
   ```bash
   chmod +x build.sh deploy.sh
   ```

2. **Build the application:**
   ```bash
   ./build.sh
   ```

3. **Run the application:**
   ```bash
   ./deploy.sh start
   ```

The chat server will be available on `localhost:12345`.

## Usage Commands

### Build Script
```bash
./build.sh                # Complete build process
```

### Deployment Script
```bash
./deploy.sh start         # Start the application
./deploy.sh stop          # Stop the application
./deploy.sh restart       # Restart the application
./deploy.sh status        # Show status
./deploy.sh logs          # Show logs
```

### Docker Commands
```bash
# Build image manually
docker build -t chatapp .

# Run container manually
docker run -d --name chatapp-server -p 12345:12345 -v $(pwd)/data:/app/data chatapp

# View logs
docker logs chatapp-server

# Stop container
docker stop chatapp-server
```

### Using Docker Compose
```bash
docker-compose up -d      # Start in background
docker-compose logs       # View logs
docker-compose down       # Stop and remove
```

## Application Details

### Server
- Runs on port 12345
- Handles user authentication (login/register)
- Manages chat rooms and message broadcasting
- Stores user data in `/app/data/users.txt`

### Client
- Connects to server on specified IP and port
- Provides GUI for chat interface
- Supports user registration and login

### Data Persistence
- User data is stored in `./data/` directory
- This directory is mounted as a Docker volume
- Data persists between container restarts

## Configuration

### Environment Variables
- `PORT`: Server port (default: 12345)
- `JAVA_OPTS`: JVM options

### Volumes
- `./data:/app/data`: User data persistence

### Ports
- `12345`: Chat server port

## Testing

### Basic Tests
1. **Container starts successfully:**
   ```bash
   docker ps | grep chatapp-server
   ```

2. **Port is accessible:**
   ```bash
   telnet localhost 12345
   ```

3. **Data persistence:**
   ```bash
   ls -la data/
   ```

### Manual Testing
1. Start the server using `./deploy.sh start`
2. Compile and run the client: `java ChatClient`
3. Register a new user
4. Send messages
5. Check that user data persists after restart

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   netstat -tulpn | grep 12345
   # Kill the process using the port
   ```

2. **Permission denied:**
   ```bash
   chmod +x *.sh
   ```

3. **Container won't start:**
   ```bash
   docker logs chatapp-server
   ```

4. **Java compilation errors:**
   ```bash
   javac -version  # Check Java version
   javac *.java    # Compile manually
   ```

### Cleanup
```bash
# Stop and remove container
docker stop chatapp-server
docker rm chatapp-server

# Remove image
docker rmi chatapp

# Clean up Docker system
docker system prune
```

## Docker Best Practices Implemented

1. **Official base image**: Using `openjdk:11-jre`
2. **Minimal layers**: Combining related commands
3. **Port exposure**: Properly exposing port 12345
4. **Volume mounting**: For data persistence
5. **Descriptive labels**: Image metadata
6. **Working directory**: Clean file organization

## Development Workflow

1. **Modify code**: Edit Java source files
2. **Rebuild**: Run `./build.sh`
3. **Test**: Run `./deploy.sh restart`
4. **Verify**: Check logs with `./deploy.sh logs`

## Production Considerations

- Use specific image tags instead of `latest`
- Implement health checks
- Configure resource limits
- Set up proper logging
- Use secrets for sensitive data
- Implement backup strategies

## Support

For issues or questions:
1. Check the logs: `./deploy.sh logs`
2. Verify container status: `./deploy.sh status`
3. Review Docker documentation
4. Check Java application logs in the data directory
