# Use official Java runtime as base image
FROM openjdk:11-jre

# Set metadata
LABEL maintainer="ChatApp Team"
LABEL version="1.0"
LABEL description="Java Chat Application"

# Set working directory
WORKDIR /app

# Copy application files
COPY *.java /app/
COPY *.class /app/

# Create data directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 12345

# Run the server
CMD ["java", "-cp", "/app", "ChatServer"]
