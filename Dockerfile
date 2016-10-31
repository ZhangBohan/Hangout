FROM python:3.5
ENV PYTHONUNBUFFERED 1
RUN wget http://download.osgeo.org/geos/geos-3.4.2.tar.bz2
RUN tar xjf geos-3.4.2.tar.bz2
WORKDIR geos-3.4.2
RUN ./configure
RUN make
RUN make install
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt -i http://pypi.douban.com/simple --trusted-host pypi.douban.com
ADD GuppiesWechat/ /code/
WORKDIR /code/GuppiesWechat
