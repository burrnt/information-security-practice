#!/bin/bash

CERT_DIR="nginx/certs"
mkdir -p "$CERT_DIR"

openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout "$CERT_DIR/selfsigned.key" \
  -out "$CERT_DIR/selfsigned.crt" \
  -subj "/C=UA/ST=Kyiv/L=Kyiv/O=University/OU=IT/CN=localhost"

echo "Self-signed сертифікат створено:"
echo "   Сертифікат: $CERT_DIR/selfsigned.crt"
echo "   Ключ:        $CERT_DIR/selfsigned.key"
