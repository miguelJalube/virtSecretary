#!/bin/bash

set -e

apt-get update && apt-get install -y git build-essential postgresql-server-dev-15

# Télécharger, compiler et installer pgvector
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
make install

# Nettoyage
cd ..
rm -rf pgvector
apt-get remove -y git build-essential postgresql-server-dev-15
apt-get autoremove -y
