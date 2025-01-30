#!/bin/bash
set -e

if [ "$NODE_TYPE" = "bootstrap" ]; then
    echo "Starting bootstrap node..."
    python -m src.cli start-bootstrap --host $HOST --port 5000
elif [ "$NODE_TYPE" = "validator" ]; then
    echo "Starting validator node..."
    python -m src.cli start --host $HOST --port 5001 --bootstrap-host $BOOTSTRAP_HOST --bootstrap-port $BOOTSTRAP_PORT --validator true
else
    echo "Starting full node..."
    python -m src.cli start --host $HOST --port 5001 --bootstrap-host $BOOTSTRAP_HOST --bootstrap-port $BOOTSTRAP_PORT
fi 
