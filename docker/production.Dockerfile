# This docker file is used for production
# Creating image based on official python3 image
FROM python:3.12.4

# Installing all python dependencies
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Get the django project into the docker container
RUN mkdir /app
RUN mkdir /app/staticfiles
RUN python manage.py collectstatic --noinput
WORKDIR /app
ADD ./ /app/