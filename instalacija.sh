#!/bin/bash

# Update i upgrade paketa
sudo apt update && sudo apt upgrade -y

# Instalacija Mininet-a
sudo apt install mininet -y

# Instalacija neophodnog Python modula
sudo pip3 install scapy

# Instalacija dodatnih alata za mrezno testiranje
sudo apt install hping3 -y

echo "Svi potrebni paketi su uspesno instalirani."
