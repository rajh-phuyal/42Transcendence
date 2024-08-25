# astein: This dockerfile will be used from the main docker-compose file
FROM nginx:1.27.0-alpine

# Expose port 80
EXPOSE 80

# Start nginx server
CMD ["nginx", "-g", "daemon off;"]
