# Use an official MongoDB base image
FROM mongo:latest

# Expose the default MongoDB port
EXPOSE 27017

# Start the MongoDB service when the container starts
CMD ["mongod"]