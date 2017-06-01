FROM python:3.6.1

RUN mkdir -p /project/app
WORKDIR /project/app

ADD ./requirements.txt /project/app/requirements.txt
RUN pip install -r requirements.txt

ADD . /project/app
CMD python manage.py runserver -h 0.0.0.0