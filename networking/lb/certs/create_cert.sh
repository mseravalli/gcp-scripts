#!/usr/bin/env bash


DOMAIN=example.marcoseravalli.com

openssl genrsa -out ${DOMAIN}.key 2048
openssl req -new -x509 -key ${DOMAIN}.key -out ${DOMAIN}.crt

openssl req -new -sha256 \
    -key ${DOMAIN}.key \
    -subj "/C=US/ST=CA/O=MyOrg, Inc./CN=${DOMAIN}" \
    -reqexts SAN \
    -config <(cat /etc/ssl/openssl.cnf \
        <(printf "\n[SAN]\nsubjectAltName=DNS:${DOMAIN}")) \
    -out ${DOMAIN}.csr

openssl x509 -req -in ${DOMAIN}.csr \
  -CA ${DOMAIN}.crt \
  -CAkey ${DOMAIN}.key \
  -CAcreateserial -out ${DOMAIN}.crt \
  -days 500 \
  -sha256
