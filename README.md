
tonenkovfoodgram.hopto.org - «Фудграм» — сайт, на котором пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

### AdminLogin
```python
lgn = admin_foodgram
psswrd = admin_foodgram
```

### Основные используемые технологии
* Python 3.9,
* Django 3.2
* PostgresSQL

### Как работать с репозиторием финального задания
    
Клонировать репозиторий и перейти в него в командной строке:
```bash
git clone https://github.com/tnkqq/foodgram.git
```

``` bash
cd foodgram/
```

Запустите весь оркестр — в терминале в папке с docker-compose.yml выполните команду:

```bash
docker-compose -f docker-compose.production.yml up
```

Выполнить миграции 
```bash 
docker compose exec backend python manage.py migrate 
```

Выгрузить данные ингредиениов и тегов из ingredients.json и tags.json

```bash 
docker compose exec backend python manage.py IngredientUpdate 
```

```bash 
docker compose exec backend python manage.py IngredientUpdate 
```

### .env  example

```
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_NAME=foodgram
DB_HOST=db
DB_PORT=5432
SECRET_KEY=
DEBUG=
ALLOWED_HOSTS=localhost,127.0.0.1
```
