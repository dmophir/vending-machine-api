# Vending Machine API
This repository describes a sample API for a simple vending machine. All users can insert coins, make purchases, and receive change back. The `seller` user can also create, update, and delete products. This API was designed based on the requirements listed in the PDF file.

## Design
The API is hosted in two Docker containers: 
- `api` which hosts the API logic in FastAPI
- `mysql`which hosts the `user` and `item` tables for authentication and inventory management

## Deploy
This API makes use of Docker-Compose for convenience. Build and run with:
```
docker compose build
docker compose run -d
```
Clean up with:
```
docker compose down
docker compose rm
```