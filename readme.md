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

pg_lsclusters
pg_ctlcluster
sudo systemctl start postgresql

database files:
/var/lib/postgresql/13/main


docker run --name my-postgres -e POSTGRES_PASSWORD=root POSTGRES_DB=tse POSTGRES_USER=hamed -d -p 5432:5432 postgres

**Redis:**

redis-cli ping

Linux:

https://redis.io/topics/quickstart

sudo /etc/init.d/redis_6379 start

MacOS:

https://gist.github.com/tomysmile/1b8a321e7c58499ef9f9441b2faa0aa8

brew services start redis
brew services stop redis


useful commands :
redis-cli
    INFO keyspace
    CONFIG GET databases
    flushall
**Celery**

celery -A kharchang.celery worker --loglevel=info
celery -A kharchang.celery beat --loglevel=info

celery -A kharchang.celery purge

celery -A kharchang.celery control shutdown


pkill -f "celery beat"
pkill -f "celery worker"

[comment]: <> (nohup celery -A kharchang.celery worker --loglevel=info > celery_worker.out &)
nohup celery -A kharchang.celery beat --loglevel=info > celery_beat.out &

celery -A kharchang.celery inspect stats


virtual environment
source venv/bin/activate

nohup celery -A kharchang.celery beat --loglevel=info > celery_beat.out &
nohup celery -A kharchang.celery worker -l info --autoscale 4,2  > celery_default_queue.out &
nohup celery -A kharchang.celery worker -l info -Q low_priority --autoscale 2,1 > celery_low_priority_queue.out &
nohup celery -A kharchang.celery worker -l info -Q high_priority --autoscale 8,4 > celery_high_priority_queue.out &


https://betterprogramming.pub/python-celery-best-practices-ae182730bb81
add.apply_async(queue='low_priority', args=(5, 5))
add.apply_async(queue='high_priority', kwargs={'a': 5, 'b': 5})
add.apply_async(queue='high_priority', priority=0, kwargs={'a': 10, 'b': 5})
add.apply_async(queue='high_priority', priority=3, kwargs={'a': 10, 'b': 5})
add.apply_async(queue='high_priority', priority=9, kwargs={'a': 10, 'b': 5})