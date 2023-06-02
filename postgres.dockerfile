# Base image
FROM postgres:latest

# Set environment variables
ENV POSTGRES_USER=user
ENV POSTGRES_PASSWORD=pass
ENV POSTGRES_DB=test

# Copy initialization script to container
# COPY tests/init.sql /docker-entrypoint-initdb.d/

# Expose the PostgreSQL port
EXPOSE 5432