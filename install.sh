#!/bin/bash

if [ "$(whoami)" != "root" ]; then
  echo "Script must be executed as root"
fi

echo "Creating directory structure"
mkdir -p /etc/amd-gpu-fan/conf

echo "Copying standard configurations and daemon"
cp ./daemon/* /etc/amd-gpu-fan/ -r

echo "Enabling daemon"
systemctl enable /etc/amd-gpu-fan/amd-gpu-fan.service
systemctl start amd-gpu-fan.service

echo "Copying bins"
mkdir -p /usr/share/amd-gpu-fan/
cp ./src/* /usr/share/amd-gpu-fan/

chmod +x ./bin/*
cp ./bin/* /usr/local/bin

echo "Running setup for gui"
current=$(pwd)
cd /usr/share/amd-gpu-fan/

python3 -m venv amd-gpu-fan-venv
source amd-gpu-fan-venv/bin/activate

python3 -m pip install -r requirements.txt
deactivate
cd $current

echo "Done"