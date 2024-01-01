if [ -e /etc/pki/tls/openssl.cnf ]
then
OPENSSL_CNF=/etc/pki/tls/openssl.cnf
elif [ -e /etc/ssl/openssl.cnf ]
then
OPENSSL_CNF=/etc/ssl/openssl.cnf
else
echo "ERROR: no openssl.cnf found"
exit 1
fi

openssl req \
    -newkey rsa:4096 \
    -x509 \
    -nodes \
    -keyout $1 \
    -new \
    -out $2 \
    -subj /CN=$(hostname) \
    -reqexts SAN \
    -extensions SAN \
    -config <(cat $OPENSSL_CNF <(printf "[SAN]\nsubjectAltName=DNS:$(hostname)")) \
    -sha256 \
    -days 3650
chmod 600 $1

# another way:
# openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 3650 -nodes -subj "/CN=localhost"