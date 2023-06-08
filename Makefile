CODE = transactions_processing

all:
	@echo "make shell\t\t\t- activate shell"
	@echo "make lint\t\t\t- check code with pylint"
	@echo "make format\t\t\t- reformat code with isort and black"
	@echo "make export\t\t\t- export dependencies to requirements.txt"
	@echo "make down\t\t\t- stop and remove containers, networks"
	@echo "make up\t\t\t\t- create and start containers"
	@echo "make up_build\t\t\t- rebuild, create and start containers"
	@echo "make restart\t\t\t- make down && make up_build"


shell:
	poetry shell

lint:
	poetry run pylint $(CODE)

format:
	poetry run isort $(CODE) $(if $(CHECK_ONLY),--check-only)
	poetry run black $(CODE) $(if $(CHECK_ONLY),--check --diff)

export:
	poetry export -f requirements.txt --without-hashes --without-urls > requirements.txt

down:
	docker compose down

up:
	docker compose up --detach

up_build:
	docker compose up --detach --build

restart: down up_build
	