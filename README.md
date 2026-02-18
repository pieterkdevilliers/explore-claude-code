# Build images (only needed after code changes)
docker compose -f docker-compose.local.yml build

# Run (after building)
docker compose -f docker-compose.local.yml up

# Build and run in one step
docker compose -f docker-compose.local.yml up --build

# Run in the background (detached)
docker compose -f docker-compose.local.yml up -d

# View logs when running detached
docker compose -f docker-compose.local.yml logs -f

# Stop containers
docker compose -f docker-compose.local.yml down

# First time only — create the superuser while containers are running:

docker compose -f docker-compose.local.yml exec backend uv run python create_superuser.py
Then visit http://localhost:3000.