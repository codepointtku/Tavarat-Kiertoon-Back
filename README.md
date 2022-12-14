# Tavarat-Kiertoon-Back

Backend for City of Turku Tavarat Kiertoon internal recycling platform.

## Docker

You need to be in the same folder as docker-compose.yml and to have Docker running on your computer for the commands to work.

`docker-compose up -d` starts and stays open in the background.

`docker-compose up --build -d` builds new images.

`docker-compose down` closes.

### How to update

`docker-compose down --rmi all` closes if open and removes the images.

On the next start Docker will rebuild the images using the new code.
