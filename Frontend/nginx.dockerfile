# astein: This dockerfile will be used from the main docker-compose file
FROM nginx:1.27.0-alpine

RUN apk update && apk add --no-cache nginx openssl

RUN mkdir /etc/nginx/ssl \
    && openssl genrsa -out /etc/nginx/ssl/barely-alive.42.fr.key \
    && openssl req -new -key /etc/nginx/ssl/barely-alive.42.fr.key -out /etc/nginx/ssl/barely-alive.42.fr.csr \
    -subj "/C=PT/ST=Lisbon/L=Lisbon/O=42Lisboa/CN=barely-alive.42.fr" \
    && openssl x509 -req -days 365 -in /etc/nginx/ssl/barely-alive.42.fr.csr \
    -signkey /etc/nginx/ssl/barely-alive.42.fr.key -out /etc/nginx/ssl/barely-alive.42.fr.crt
    
COPY ./assets/default_avatar.png ./media/avatars/default_avatar.png

# Expose port 80
EXPOSE 443

# Start nginx server
CMD ["nginx", "-g", "daemon off;"]
