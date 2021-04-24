**Installing MongoDb**

Linux:

https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/

sudo systemctl start mongod
sudo systemctl status mongods
sudo systemctl restart mongod

MacOS:

https://docs.mongodb.com/manual/tutorial/install-mongodb-on-os-x/

as a background service: 
brew services start mongodb/brew/mongodb-community

simple: mongod --config /usr/local/etc/mongod.conf

brew services start postgresql

**Redis:**

redis-cli ping

Linux:

https://redis.io/topics/quickstart

sudo /etc/init.d/redis_6379 start

MacOS:

https://gist.github.com/tomysmile/1b8a321e7c58499ef9f9441b2faa0aa8

brew services start redis
brew services stop redis

**Celery**

celery -A kharchang.celery worker --loglevel=info
celery -A kharchang.celery beat --loglevel=info

celery -A kharchang.celery purge

celery -A kharchang.celery control shutdown


pkill -f "celery beat"
pkill -f "celery worker"
nohup celery -A kharchang.celery worker --loglevel=info > celery_worker.out &
nohup celery -A kharchang.celery beat --loglevel=info > celery_beat.out &