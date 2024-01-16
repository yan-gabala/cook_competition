Всем фудпривет!

Tecnhologies
Python 3.9
Django 3.2
Django REST framework
Nginx
Docker
Postgres
http://devinse.ru   http://130.193.53.39  Логин w@w.ru   Пароль w

Здесь вы можете поделиться рецептами блюд, добавить их в избранное и вывести список покупок для приготовления любимых блюд. Для сохранения порядка - создавать теги и ингредиенты разрешено только администраторам.

Также есть API. Для просмотра доступных путей перейдите по ссылке: http://devinse.ru/api/.

Документация API здесь.: http://devinse.ru/api/docs/.

Для развертывания этого проекта необходимы следующие действия:

Загрузите проект с помощью SSH:
git clone https://github.com/yan-gabala/foodgram-project-react.git
Настройте коннект с вашим сервером:
ssh <server user>@<server IP>
Установите Docker:
sudo apt install docker.io

Установите Docker Compose (for Linux):
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

Получите permissions для docker-compose:
sudo chmod +x /usr/local/bin/docker-compose

Создайте каталог проекта (желательно в вашем домашнем каталоге):
mkdir foodgram && cd foodgram/

Создайте env-file:
touch .env

Заполните env-файл вот так:
DEBUG=False
SECRET_KEY=<Your_some_long_string>
ALLOWED_HOSTS=<Your_host>
CSRF_TRUSTED_ORIGINS=https://<Your_host>
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<Your_password>
DB_HOST=foodgram-db
DB_PORT=5432

Скопируйте файлы из 'infra/' вашей локальной машины на ваш сервер:
scp -r infra/* <server user>@<server IP>:/home/<server user>/foodgram/

Запустите docker-compose:
sudo docker-compose up -d

Можете создать суперюзера:
sudo docker exec -it app python manage.py createsuperuser

При желании вы можете использовать список ингредиентов для написания рецептов. Загрузите его в базу данных с помощью следующей команды:

sudo docker compose exec -T backend python manage.py load_ingredients

Автор: Сергей Виноградов
