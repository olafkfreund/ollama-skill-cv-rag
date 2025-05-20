#!/bin/bash

set -e

# Domain and email configuration
domain="home.freundcloud.com"
email="olaf@freundcloud.com"
staging=1 # Set to 1 for testing, 0 for production

# Remove existing containers and volumes
echo "### Cleaning up existing setup ..."
docker compose down -v

echo "### Creating Docker volumes ..."
docker volume create ollama-rag_certbot_conf
docker volume create ollama-rag_certbot_www

echo "### Starting nginx ..."
docker compose up -d nginx

echo "### Requesting Let's Encrypt certificate for $domain ..."
# Select appropriate email arg
case "$email" in
  "") email_arg="--register-unsafely-without-email" ;;
  *) email_arg="--email $email" ;;
esac

# Enable staging mode if needed
if [ $staging != "0" ]; then 
  staging_arg="--staging"
  echo "### Using staging environment ..."
fi

# Request the certificate
docker compose run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
    $staging_arg \
    $email_arg \
    -d $domain \
    --rsa-key-size 4096 \
    --agree-tos \
    --force-renewal \
    --verbose" certbot

echo "### Reloading nginx ..."
docker compose exec nginx nginx -s reload

echo "### Starting certbot renewal service ..."
docker compose up -d certbot

echo "
Certificate setup completed!
"
