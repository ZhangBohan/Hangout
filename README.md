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
当前项目使用Docker部署，分为生产和测试两个容器。

### 生产

#### 代码
位于/opt/HangoutOnline/Hangout，如需更新代码直接通过`git pull`将代码更新到最新即可。
共3个服务，通过默认`docker-compose.yml`进行管理，

- web 线上Django服务器
- db 线上数据库
- metabase 数据分析服务

#### 启动
```
cd /opt/HangoutOnline/Hangout
docker-compose up -d
```

#### 数据库访问
```
docker-compose run db psql -h db -U postgres postgres
```
#### 日志查看
```
docker-compose logs -f
```
可指定具体服务查看
```
docker-compose logs -f web
```

### 测试

#### 代码
位于/opt/HangoutTest/Hangout，如需更新代码或切换分支直接通过`git`命令操作即可。
共2个服务，通过默认`docker-compose-test.yml`进行管理，

- test_web 线上Django服务器
- test_db 线上数据库

#### 启动
```
cd /opt/HangoutTest/Hangout
docker-compose -f docker-compose-test.yml up -d
```

#### 重启测试服务器
```
docker-compose restart test_web
```

#### 删除测试数据库并重启
```
docker-compose stop test_db
docker-compose rm test_db
rm -r .data/test_postgres/
docker-compose up -d
```

#### 数据库访问
```
docker-compose -f docker-compose-test.yml run test_db psql -h test_db -U postgres postgres
```

#### 日志查看
```
docker-compose -f docker-compose-test.yml logs -f
```
可指定具体服务查看
```
docker-compose -f docker-compose-test.yml logs -f test_web
```

