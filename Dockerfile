FROM awesto/fedora-uwsgi-python:24.1

LABEL Description="Run django-angular demo" Maintainer="Jacob Rief <jacob.rief@gmail.com>"

# install and configure Redis
RUN dnf install -y redis
RUN mkdir -p /web/redis
COPY docker-files/redis.ini /etc/uwsgi.d/redis.ini
COPY docker-files/redis.conf /etc/redis.conf
RUN chown redis.redis /etc/uwsgi.d/redis.ini
RUN chown -R redis.redis /web/redis

RUN useradd -M -d /web -g uwsgi -s /bin/bash django

# install the basic Django package
RUN echo 2 | alternatives --config python
RUN python -V
RUN pip install --upgrade pip
# RUN pip install --force-reinstall uwsgi
RUN pip install django==1.10.7

# copy the local django-angular file into a temporary folder
RUN mkdir -p /tmp/django-angular
COPY LICENSE.txt /tmp/django-angular
COPY README.md /tmp/django-angular
COPY MANIFEST.in /tmp/django-angular
COPY setup.py /tmp/django-angular
ADD djng /tmp/django-angular/djng
# and from there install it into the site-package using setup.py
RUN pip install /tmp/django-angular
RUN rm -rf /tmp/django-angular

# create the example project
RUN mkdir -p /web/workdir/{media,static}
ADD examples/server /web/django-angular-demo/server
ADD client /web/django-angular-demo/client
COPY docker-files/wsgi_runserver.py /web/django-angular-demo/wsgi_runserver.py
COPY docker-files/wsgi_websocket.py /web/django-angular-demo/wsgi_websocket.py
COPY examples/manage.py /web/django-angular-demo/manage.py
COPY examples/package.json /web/django-angular-demo/package.json
COPY examples/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
RUN pip install django-websocket-redis

# install packages outside of PyPI
WORKDIR /web/django-angular-demo
RUN npm install

# add uwsgi.ini file into workdir, so that touching this file restarts the Django server
COPY docker-files/uwsgi-emperor.ini /etc/uwsgi.ini
COPY docker-files/uwsgi-websocket.ini /web/workdir/uwsgi-websocket.ini
RUN ln -s /web/workdir/uwsgi-websocket.ini /etc/uwsgi.d/djangular-websocket.ini
COPY docker-files/uwsgi-runserver.ini /web/workdir/uwsgi-runserver.ini
RUN ln -s /web/workdir/uwsgi-runserver.ini /etc/uwsgi.d/djangular-runserver.ini

# collect static files
RUN CLIENT_SRC_DIR=/web/django-angular-demo/client/src NODE_MODULES_DIR=/web/django-angular-demo/node_modules DJANGO_STATIC_ROOT=/web/workdir/static ./manage.py collectstatic --noinput
RUN chown -R django.uwsgi /web/{logs,workdir}

# share media files
VOLUME /web/workdir/media

# when enabling the CMD disable deamonize in uwsgi.ini
EXPOSE 9002
CMD ["/usr/sbin/uwsgi", "--ini", "/etc/uwsgi.ini"]
