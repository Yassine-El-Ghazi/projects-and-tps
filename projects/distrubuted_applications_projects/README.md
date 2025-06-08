# Chat Application Docker Deployment

This project provides Docker containerization for a Java-based chat application with separate server and client components.

## 📋 Project Structure

```
├── ChatServer.java          # Server application source
├── ChatClient.java          # Client application source  
├── ChatProtocol.java        # Common protocol interface
├── Dockerfile.server        # Server Docker image
├── Dockerfile.client        # Client Docker image
├── docker-compose.yml       # Docker Compose configuration
├── build.sh                # Automated build script
├── deploy.sh               # Deployment script
├── test.sh                 # Testing script
└── README.md               # This documentation
```

## 🚀 Quick Start

### Prerequisites
- Docker installed and running
- Java 11+ for compilation
- Network access for Docker Hub

### 1. Build the Application

```bash
# Make scripts executable
chmod +x build.sh deploy.sh test.sh

# Build Docker images
./build.sh
```

### 2. Deploy the Application

```bash
# Start the server
./deploy.sh start-server

# Start a client (in another terminal)
./deploy.sh start-client
```

### 3. Test the Deployment

```bash
# Run validation tests
./test.sh
```

## 🐳 Docker Images

### Server Image (`chat-server:latest`)
- **Base**: `openjdk:11-jre-slim`
- **Port**: 12345
- **Features**:
  - Lightweight JRE-only image
  - Persistent data volume support
  - Health check integration
  - Configurable memory settings

### Client Image (`chat-client:latest`)
- **Base**: `openjdk:11-jre-slim`
- **Features**:
  - GUI support with X11
  - Virtual display (Xvfb)
  - Window manager (Fluxbox)
  - Network connectivity to server

## 📖 Usage Guide

### Manual Docker Commands

#### Start Server
```bash
# Create network
docker network create chat-network

# Create data volume
docker volume create chat-data

# Run server
docker run -d \
  --name chat-server \
  --network chat-network \
  -p 12345:12345 \
  -v chat-data:/app/data \
  chat-server:latest
```

#### Start Client
```bash
# Run client
docker run -d \
  --name chat-client-1 \
  --network chat-network \
  -e DISPLAY=:99 \
  chat-client:latest
```

### Using Docker Compose

```bash
# Start server only
docker-compose up -d chat-server

# Start server and client
docker-compose --profile client up -d
```

### Using Deployment Scripts

```bash
# Available commands
./deploy.sh help

# Start components
./deploy.sh start-server
./deploy.sh start-client

# Monitor
./deploy.sh status
./deploy.sh logs-server
./deploy.sh logs-client

# Stop everything
./deploy.sh stop

# Complete cleanup
./deploy.sh cleanup
```

## 🔧 Configuration

### Environment Variables

#### Server Container
- `JAVA_OPTS`: JVM options (default: `-Xmx256m -Xms128m`)

#### Client Container
- `DISPLAY`: X11 display (default: `:99`)

### Volumes

- `chat-data`: Persistent storage for user data and chat history
- Mount point: `/app/data`

### Networks

- `chat-network`: Bridge network for inter-container communication

## 🧪 Testing

The test script validates:
- Docker availability
- Image existence and sizes
- Container startup
- Network connectivity
- Volume operations
- Docker Compose configuration

```bash
./test.sh
```

## 📊 Monitoring

### Check Container Status
```bash
docker ps --filter "name=chat-"
```

### View Logs
```bash
# Server logs
docker logs -f chat-server

# Client logs  
docker logs -f chat-client-1
```

### Resource Usage
```bash
docker stats chat-server chat-client-1
```

## 🛠️ Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find process using port 12345
lsof -i :12345

# Change port mapping
docker run -p 12346:12345 chat-server:latest
```

#### Client GUI Issues
```bash
# Check X11 setup
docker exec -it chat-client-1 ps aux | grep Xvfb

# Restart client with new display
docker run -e DISPLAY=:100 chat-client:latest
```

#### Network Connectivity
```bash
# Test network
docker network inspect chat-network

# Recreate network
docker network rm chat-network
docker network create chat-network
```

#### Volume Permissions
```bash
# Check volume
docker volume inspect chat-data

# Fix permissions
docker run --rm -v chat-data:/data alpine chown -R 1000:1000 /data
```

### Cleanup Commands

```bash
# Remove all chat containers
docker rm -f $(docker ps -aq --filter "name=chat-")

# Remove images
docker rmi chat-server:latest chat-client:latest

# Remove volumes
docker volume rm chat-data

# Remove network
docker network rm chat-network
```

## 🔒 Security Considerations

- Server runs as non-root user
- Minimal base images used
- No unnecessary packages installed
- Network isolation with custom bridge
- Volume permissions properly configured

## 📈 Performance Optimization

- JVM memory limits configured
- Image layers optimized
- Health checks implemented
- Restart policies configured
- Resource constraints can be added

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Test with `./test.sh`
4. Submit pull request

## 📄 License

This project is provided as-is for educational use. Modify and extend freely.

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review container logs
3. Run the test script
4. Create an issue with full error details
