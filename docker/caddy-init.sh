#!/bin/sh
set -e

DOMAIN="${DOMAIN:-localhost}"
EMAIL="${EMAIL:-admin@localhost}"

sed "s|{env.DOMAIN}|${DOMAIN}|g; s|{env.EMAIL}|${EMAIL}|g" /etc/caddy/Caddyfile > /tmp/Caddyfile

exec caddy run --config /tmp/Caddyfile --adapter caddyfile
