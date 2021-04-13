**Installing MongoDb**

Linux:

https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/

sudo systemctl start mongod
sudo systemctl status mongod
sudo systemctl stop mongod
sudo systemctl restart mongod

MacOS:

https://docs.mongodb.com/manual/tutorial/install-mongodb-on-os-x/

as a background service: 
brew services start mongodb/brew/mongodb-community

simple: mongod --config /usr/local/etc/mongod.conf

brew services start postgresql

**Redis:**

Linux:

https://redis.io/topics/quickstart

sudo /etc/init.d/redis_6379 start

MacOS:

https://gist.github.com/tomysmile/1b8a321e7c58499ef9f9441b2faa0aa8

brew services start redis
brew services stop redis


**Dajngo Dynamic Scrapper**

https://django-dynamic-scraper.readthedocs.io/

pip install django-dynamic-scraper