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



# How to change style:
If you are planning to work on langing page design/style look at this files:
1. https://github.com/cpfed/diploma-cpfed-auth/blob/master/templates/base.html#L11C6-L11C56
2. You can create your own style file in the folder static (https://github.com/cpfed/diploma-cpfed-auth/tree/master/static)
3. Lets say you named it mystyle.css and put it in the folder static/mystyle.css
4. Just replace
```
<script src="https://cdn.tailwindcss.com"></script>
```
with
```
<link rel="stylesheet" href="{% static 'mystyle.css' %}" >
```


