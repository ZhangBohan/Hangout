FROM python:3.5
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt -i http://pypi.douban.com/simple --trusted-host pypi.douban.com
ADD GuppiesWechat/ /code/
WORKDIR /code/GuppiesWechat
