FROM ubuntu:14.04

FROM python:3
MAINTAINER arnaud@codekraft.fr

RUN mkdir -p /app
COPY gunicorn_config.py /app/gunicorn_config.py

WORKDIR /app

RUN pip install alembic==0.9.5
RUN pip install bcrypt==3.1.3
RUN pip install cffi==1.10.0
RUN pip install click==6.7
RUN pip install coverage==4.4.1
RUN pip install Flask==0.12.2
RUN pip install Flask-Bcrypt==0.7.1
RUN pip install Flask-Migrate==2.1.0
RUN pip install Flask-Script==2.0.5
RUN pip install Flask-SQLAlchemy==2.2
RUN pip install Flask-Testing==0.6.2
RUN pip install ForgeryPy==0.1
RUN pip install itsdangerous==0.24
RUN pip install Jinja2==2.9.6
RUN pip install Mako==1.0.7
RUN pip install MarkupSafe==1.0
RUN pip install nose==1.3.7
RUN pip install psycopg2==2.7.3
RUN pip install pycparser==2.18
RUN pip install PyJWT==1.5.2
RUN pip install python-dateutil==2.6.1
RUN pip install python-editor==1.0.3
RUN pip install six==1.10.0
RUN pip install SQLAlchemy==1.1.13
RUN pip install Werkzeug==0.12.2
RUN pip install gunicorn

EXPOSE 8000

CMD [ "gunicorn", "-b", "0.0.0.0", "app:app" ]
