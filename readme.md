Проект: Сайт интернет-магазина

Мусаэлян Карлен

KarlosGsalva

karlenmusaelian@gmail.com

Для запуска проекта:

docker-compose -f docker-compose.yml up --build

docker-compose -f docker-compose.yml exec django python manage.py makemigrations

docker-compose -f docker-compose.yml exec django python src/manage.py migrate

docker-compose -f docker-compose.yml exec django python src/manage.py createsuperuser