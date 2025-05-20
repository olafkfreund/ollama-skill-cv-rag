FROM caddy:2-alpine

# Install additional tools for debugging
RUN apk add --no-cache curl shadow

# Create caddy user and group
RUN groupadd -g 1000 caddy && \
    useradd -u 1000 -g caddy -s /sbin/nologin -M caddy

# Create directory structure
RUN mkdir -p /srv/static /srv/assets /data/caddy /config/caddy

# Copy configurations and static files
COPY docker/Caddyfile /etc/caddy/Caddyfile
COPY static /srv/static
COPY templates /srv/templates
COPY assets /srv/assets

# Set up permissions
RUN chown -R caddy:caddy /srv /data /config /etc/caddy && \
    chmod -R 755 /srv/static /srv/templates /srv/assets

# Set environment variables
ENV XDG_DATA_HOME=/data
ENV XDG_CONFIG_HOME=/config

# Expose Caddy admin interface
EXPOSE 80 443 2019

# Switch to caddy user
USER caddy
