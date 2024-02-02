## Проект «Foodgram»

***

### Описание:
Cайт Foodgram, «Продуктовый помощник». На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.
***
### Системные требования:
- Python 3.11.5.
- Docker
- nginx
- kkk
***
### Установка:

1. Склонируйте репозиторий по ссылке:
```
git clone git@github.com:Freelancerroma/foodgram-project-react.git
```
2. В корневом каталоге создайте файл .env и добавьте необходимые данные:
* POSTGRES_DB=foodgram # Задаем имя для БД.
* POSTGRES_USER=foodgram_user # Задаем пользователя для БД.
* POSTGRES_PASSWORD=foodgram_password # Задаем пароль для БД.
* DB_HOST=db
* DB_PORT=5432
* DEBUG_MODE=False
* SECRET_KEY=django-insecure
* ALLOWED_HOSTS=127.0.0.1 localhost # Задаем свой IP сервера, DNS имя
* CSRF_TRUSTED_ORIGINS=http://127.0.0.1 http://localhost # Задаем свой IP сервера, DNS имя

3. Подготовьте Secrets->Actions в репозитории проекта на GitHub:
* DOCKER_PASSWORD         # пароль от Docker Hub
* DOCKER_USERNAME         # логин Docker Hub
* HOST                    # публичный IP сервера
* USER                    # имя пользователя на сервере
* PASSPHRASE              # *если ssh-ключ защищен паролем
* SSH_KEY                 # приватный ssh-ключ
* TELEGRAM_TO             # ID телеграм-аккаунта для посылки сообщения
* TELEGRAM_TOKEN          # токен бота, посылающего сообщение

4. На удаленном сервере установите Docker и Docker Compose выполнив следующие команды:
```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt install docker-compose-plugin
```

5. На удаленном сервере установите nginx выполнив следующие команды:
```
sudo apt install nginx -y 
sudo systemctl start nginx
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

6. Создайте директорию на сервере для вашего проекта (в данном случае foodgram, см. .github/workflows/main.yml) и скопируйте туда файл .env.

7. После выполнения команды git push на GitHub, запустится файл .github/workflows/main.yml, который выполнит необходимые операции по сборке образов и созданию контейнеров на удаленном сервере при помощи docker-compose.production.yml.

8. Перейдите на запущенный контейнер foodgram_backend и создайте суперпользователя:
```
docker exec -it foodgram_backend bash
```
```
python manage.py createsuperuser
```

9. Настройте nginx в соответствии с нужным портом (см. backend/foodgram/Dockerfile) и перезапустите его:
```
sudo systemctl reload nginx
```

10. Теперь проект доступен по вашему IP (http://<Ваш IP>:9090) или по вашему DNS, а также спецификация API по адресу:
```
http://<Ваш IP>:9090/api/docs/
```

### Инструменты и стек:
- Python
- JSON
- YAML
- Django
- React
- Telegram
- API
- Docker
- Nginx
- PostgreSQL
- Gunicorn
- JWT
- Postman

Автор: [Недосеко Роман](https://github.com/freelancerroma)
