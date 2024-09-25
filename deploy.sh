#!/bin/bash
# Pull the latest code from the Git repository
echo "Pulling latest code from Git..."
git pull origin prod

# Install new dependencies if any
echo "Installing dependencies..."
pip install -r requirements.txt

# Run database migrations
echo "Running database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Restart Gunicorn
echo "Restarting Gunicorn..."
sudo systemctl restart gunicorn

# Deployment finished
echo "Deployment complete!"
