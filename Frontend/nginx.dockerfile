# astein: This dockerfile will be used from the main docker-compose file
FROM nginx:1.27.0-alpine

# Install necessary packages and OpenSSL
RUN apk update && apk add --no-cache nginx openssl gettext

# Create directories for media files and nginc.config files
RUN mkdir -p  /media/avatars /tmp/nginx/ /tools/

# Copy the media files
COPY ./assets/avatars/* /media/avatars/

# Copy configuration files
COPY ./nginx/nginx.conf /etc/nginx/nginx.conf

# Copy the entrypoint.sh, make it excutable and run it
COPY ./tools/entrypoint.sh /tools/entrypoint.sh
RUN chmod +x /tools/entrypoint.sh
ENTRYPOINT ["/tools/entrypoint.sh"]

# Copy the healthcheck.sh, make it excutable and run it
COPY ./tools/healthcheck.sh /tools/healthcheck.sh
RUN chmod +x /tools/healthcheck.sh

# Expose port 80
EXPOSE 443

# Start nginx server
CMD ["nginx", "-g", "daemon off;"]





#RUN mkdir /etc/nginx/ssl \
#    && openssl genrsa -out /etc/nginx/ssl/barely-alive.42.fr.key \
#    && openssl req -new -key /etc/nginx/ssl/barely-alive.42.fr.key -out /etc/nginx/ssl/barely-alive.42.fr.csr \
#    -subj "/C=PT/ST=Lisbon/L=Lisbon/O=42Lisboa/CN=barely-alive.42.fr" \
#    && openssl x509 -req -days 365 -in /etc/nginx/ssl/barely-alive.42.fr.csr \
#    -signkey /etc/nginx/ssl/barely-alive.42.fr.key -out /etc/nginx/ssl/barely-alive.42.fr.crt

#COPY ahok.cool_private_key.key /etc/nginx/ssl/barely-alive.42.fr.key
#COPY ahok.cool_ssl_certificate.cer /etc/nginx/ssl/barely-alive.42.fr.crt


