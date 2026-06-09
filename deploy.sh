#!/bin/bash

set -e

APP_NAME="cypherqube"

SOURCE_DIR="$WORKSPACE"
DEPLOY_DIR="/opt/$APP_NAME"

echo "[+] Removing old deployment..."
rm -rf "$DEPLOY_DIR"

echo "[+] Creating deployment directory..."
mkdir -p "$DEPLOY_DIR"

echo "[+] Copying files..."
cp -r "$SOURCE_DIR"/* "$DEPLOY_DIR"

echo "[+] Deployment complete"

echo "[+] Current files:"
ls -la "$DEPLOY_DIR"
