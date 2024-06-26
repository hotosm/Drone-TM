#!/bin/bash

# Update the system
apt update && apt upgrade -y

# Install software
snap install docker
apt install awscli postgresql-client

# Add docker permissions for ssm-user
#groupadd -g 1005 docker
#usermod -a -G docker ssm-user

# Reboot the system
sleep 10
reboot
