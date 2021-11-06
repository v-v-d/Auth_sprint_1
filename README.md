![tests](https://github.com/v-v-d/Auth_sprint_1/actions/workflows/tests.yml/badge.svg)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

# Сервис аутентификации и авторизации
TODO: [Auth_sprint_1#6](https://github.com/v-v-d/Auth_sprint_1/issues/6)

## Общие правила aka code-style
1. Вся бизнес-логика должна помещаться в провайдерах src/app/services
2. Модели содержат только описание таблиц и специализированные методы по запросам в таблицы
3. Эндпоинты обращаются к провайдеру и вызывают у него необходимый метод. Результат эндпоинта - 
результат работы метода провайдера, т.е. или какая-то структура или исключение 

## Запуск
1. Создать общую сеть для всех проектов практикума, чтобы была связь между всеми контейнерами курса
```shell
sudo docker network create yandex
```
2. Собрать и запустить текущий проект
```shell
sudo docker-compose up --build
```
3. Перейти к документации по адресу 0.0.0.0

## Тестирование
Собрать тестовое окружение и запустить тесты
```shell
sudo docker-compose -f docker-compose.test.yaml up --build
```



