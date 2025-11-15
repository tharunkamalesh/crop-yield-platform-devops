# Use Nginx as base image
FROM nginx:alpine

# Remove default nginx config
RUN rm -rf /etc/nginx/conf.d/*

# Copy custom nginx config
COPY frontend/nginx.conf /etc/nginx/conf.d/

# Copy built React app
COPY frontend/build/ /usr/share/nginx/html/

# Expose port 3000
EXPOSE 3000

# Start nginx
CMD ["nginx", "-g", "daemon off;"]