#!/bin/bash

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
echo "deb [arch=amd64] https://download.docker.com/linux/ubuntu xenial stable" > /etc/apt/sources.list.d/docker.list
sudo apt update && sudo apt install docker-ce python3 python3-pip
sudo usermod -aG docker ${USER}
sudo pip3 install docker requests 

echo "Now install ctfdbot"
