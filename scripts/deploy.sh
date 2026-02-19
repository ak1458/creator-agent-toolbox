#!/bin/bash
# Deployment script for Creator Agent Toolbox

set -e

echo "🚀 Creator Agent Toolbox - Deployment Script"
echo "=============================================="

# Check environment
if [ -z "$ENVIRONMENT" ]; then
    echo "⚠️  ENVIRONMENT not set, defaulting to 'development'"
    export ENVIRONMENT=development
fi

echo "📦 Environment: $ENVIRONMENT"

# Function to deploy to development
deploy_dev() {
    echo "🔧 Deploying to Development..."
    
    # Install dependencies
    cd backend
    poetry install
    
    # Run migrations
    poetry run alembic upgrade head
    
    # Start server
    echo "🌐 Starting development server..."
    poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

# Function to deploy with Docker
deploy_docker() {
    echo "🐳 Deploying with Docker..."
    
    # Build and start services
    docker-compose down
    docker-compose up --build -d
    
    # Wait for services to be healthy
    echo "⏳ Waiting for services..."
    sleep 10
    
    # Run migrations
    docker-compose exec -T backend poetry run alembic upgrade head
    
    echo "✅ Deployment complete!"
    echo "📊 Backend: http://localhost:8000"
    echo "🗄️  Adminer (DB): http://localhost:8080"
}

# Function to show logs
show_logs() {
    docker-compose logs -f
}

# Main command handler
case "${1:-dev}" in
    dev)
        deploy_dev
        ;;
    docker)
        deploy_docker
        ;;
    logs)
        show_logs
        ;;
    migrate)
        cd backend
        poetry run alembic upgrade head
        ;;
    *)
        echo "Usage: $0 [dev|docker|logs|migrate]"
        echo ""
        echo "Commands:"
        echo "  dev     - Run development server locally"
        echo "  docker  - Deploy with Docker Compose"
        echo "  logs    - Show Docker logs"
        echo "  migrate - Run database migrations"
        exit 1
        ;;
esac
