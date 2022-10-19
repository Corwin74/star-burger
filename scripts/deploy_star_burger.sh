#!/bin/bash

set -e

cd star-burger/
source ~/star-burger.env/bin/activate
git pull -q
pip install -q -r requirements.txt
/home/burger/.nvm/versions/node/v16.17.1/bin/npm ci --include=dev > /dev/null 2>&1 
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./" > /dev/null 2>&1
python manage.py collectstatic --noinput -v 0
python manage.py migrate --noinput -v 0
sudo /usr/bin/systemctl restart postgresql.service
sudo /usr/bin/systemctl restart gunicorn.socket
sudo /usr/bin/systemctl reload nginx.service
https -q POST https://api.rollbar.com/api/1/deploy X-Rollbar-Access-Token:70cf93059b834d44b9f188a50b81e42c \
                        Content-Type:application/json environment=ruvds revision=$(git rev-parse HEAD) \
                        local_username=burger status=succeeded
echo Deploy complete!
