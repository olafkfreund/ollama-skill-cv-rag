FROM nginx:alpine

# Remove default nginx static content
RUN rm -rf /usr/share/nginx/html/*

# Copy static files and assets
COPY static/index.html /usr/share/nginx/html/index.html
COPY assets /usr/share/nginx/html/assets

# Set permissions and ownership for Nginx user
RUN chmod -R 755 /usr/share/nginx/html && \
    chown -R nginx:nginx /usr/share/nginx/html

# Fix permissions for Nginx temp/cache directories
RUN mkdir -p /var/cache/nginx /var/run /var/log/nginx && \
    chown -R nginx:nginx /var/cache/nginx /var/run /var/log/nginx

# Copy custom nginx config
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY docker/nginx.main.conf /etc/nginx/nginx.conf

# Override pid file location for non-root user
# (must match in nginx.conf)

EXPOSE 80

# Use non-root user for security
USER nginx

CMD ["nginx", "-g", "daemon off;"]
