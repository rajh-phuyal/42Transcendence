# astein: This dockerfile will be used from the main docker-compose file
FROM nginx:1.27.0-alpine

# Install necessary packages and OpenSSL
RUN apk update && apk add --no-cache nginx openssl gettext

# Create directories for media files and nginc.config files
RUN mkdir -p  /media/avatars /tmp/nginx/ /tools/

# Copy the media files
COPY ./assets/avatars/* /media/avatars/

# Copy the html files
COPY ./html/* /usr/share/nginx/html/

# Copy the css files
COPY ./css/* /usr/share/nginx/css/

# Copy the js files
COPY ./js/* /usr/share/nginx/js/

# Copy the assets files
COPY ./assets/ /usr/share/nginx/assets/


# Copy configuration files
COPY ./nginx/nginx.conf /etc/nginx/nginx.conf

# Copy the generate_ssl.sh
COPY ./tools/generate_ssl.sh /tools/generate_ssl.sh
RUN chmod +x /tools/generate_ssl.sh

# Copy the healthcheck.sh, make it excutable and run it
COPY ./tools/healthcheck.sh /tools/healthcheck.sh
RUN chmod +x /tools/healthcheck.sh

# Copy the entrypoint.sh, make it excutable and run it
COPY ./tools/entrypoint.sh /tools/entrypoint.sh
RUN chmod +x /tools/entrypoint.sh
ENTRYPOINT ["/tools/entrypoint.sh"]

# Expose port 80
EXPOSE 443

# Start nginx server
CMD ["nginx", "-g", "daemon off;"]