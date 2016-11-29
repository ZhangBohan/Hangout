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


## Deploy

当前项目中共有5个服务,通过`docker-compose.yml`进行管理, 其中:

- web 线上Django服务器
- db 线上数据库
- test_web 测试Django服务器
- test_db 测试数据库
- metabase 数据分析服务

### 部署新项目

```
cd /opt/Hangout
git clone git@github.com:AwesomeGuppies/Hangout.git
docker-compose up -d

```

### 数据库访问

测试数据库

```
docker-compose run test_db psql -h test_db -U postgres postgres
```

生产数据库

```
docker-compose run db psql -h db -U postgres postgres
```


### 测试服务器

测试服务器和本地的开发环境完全相同, 如需更新代码直接通过`git pull`将代码更新到最新即可。

执行`manage`命令:

```
docker-compose run test_web python manage.py
```

重启服务器

```
docker-compose restart test_web
```

删除测试数据库并重启

```
docker-compose stop test_db
docker-compose rm test_db
rm -r .data/test_postgres/
docker-compose up -d
```


### 日志查看

```
docker-compose logs -f
```

可以通过指定具体的服务来查看指定服务器的日志

```
docker-compose logs -f test_web
```
