#!/bin/sh
set -e

until redis-cli ping > /dev/null 2>&1; do
  echo "Waiting for Redis..."
  sleep 1
done
echo "Redis is ready!"

echo "Collect static files."
python manage.py collectstatic --no-input

echo "Run migrations."
python manage.py migrate --no-input

echo "Compile translation messages."
python manage.py compilemessages --ignore=venv --ignore=.git

python manage.py generatedata

echo "Starting..."
exec "$@"