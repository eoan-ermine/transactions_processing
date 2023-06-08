# transactions_processing

## Требования

### Требования для разработчиков

1. [python 3.10](https://www.python.org/)
2. [poetry](https://python-poetry.org/) (опционально)

### Требования для развертывания

1. [docker](https://www.docker.com/)

## Инструкция по развертыванию

```shell
cp .env.example .env
# После чего в файле .env необходимо заполнить все переменные окружения корректными значениями

make up_build
```

## Инструкция по поддержке

1. `make lint` — проверка кода с помощью `pylint`
2. `make format` — форматирование кода с помощью `isort` и `black`
3. `make export` — экспортирование зависимостей, прописанных в `pyproject.toml`, в `requirements.txt`
