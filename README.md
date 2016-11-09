# Hangout

## How to start this project

### Docker

```
docker-compose run web python manage.py migrate
docker-compose up
```

### Mac

```
brew install python3 postgresql postgis
createuser --interactive
sudo pip install virtualenv
virtualenv .env -p python3
source .env/bin/activate
pip install -r requirements.txt -i http://pypi.douban.com/simple --trusted-host pypi.douban.com
./manage.py migrate
./manage.py runserver
```
