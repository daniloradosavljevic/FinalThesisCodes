#!/bin/bash
# Kreiraj glavni folder za Flask aplikaciju
mkdir flaskapp
cd flaskapp

# Kreiraj folder za Hardhat projekat
mkdir hardhatproj
cd hardhatproj
# Inicijalizuj novi Node.js projekat i instaliraj Hardhat
npm init -y
npm install --save--dev hardhat
#Pokreni Hardhat i kreiraj osnovni projekat
npx hardhat
# Vratite se u glavni folder za Flask aplikaciju
cd ..

pip3 install Flask
# Instaliraj Puppeteer globalno
npm install -g puppeteer

echo "Instalacija je zavrsena."