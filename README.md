# Local setup


1. Copy env files and modify if required
```
cp .env.example .env
```
2. Run docker compose
```
docker compose up
```
You can access website at http://0.0.0.0:8000/

3. In separate terminal run migration
```
docker compose exec django python manage.py migrate
```


# How to access shell
While keeping docker compose up run:
```
docker compose exec -it django /bin/bash
```

# How to create superuser
While keeping docker compose up run:
```
docker compose exec django python manage.py createsuperuser
```
You can access website admin page  at http://0.0.0.0:8000/admin



