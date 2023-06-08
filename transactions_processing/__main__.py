# pylint ошибочно выдает ошибку, что не может найти psycopg2 и transactions_processing.config
# pylint: disable=import-error

import csv
import itertools

import psycopg2
import requests

from transactions_processing.config import db_host, db_name, db_password, db_port, db_user

source_files = ["clients.csv", "currency.csv", "amount.csv"]
contents = []
CLIENTS_IDX, CURRENCY_IDX, AMOUNT_IDX = 0, 1, 2

for source_file in source_files:
    # Наиболее эффективное решение: предварительно создать set и пополнять его вручную
    # Если мы напишем что-то вроде set([value for value in values]), то у нас будут лишние расходы
    # на формирование списка
    values = set()
    with open(f"data/{source_file}", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            # В каждой строке есть как минимум один элемент, поэтому все безопасно
            values.add(row[0])
    contents.append(list(values))

# Преобразуем все элементы amount в числовые значения
contents[AMOUNT_IDX] = [int(amount) for amount in contents[AMOUNT_IDX]]

# Формируем все уникальные варианты сочетаний переменных из всех файлов
transactions = list(itertools.product(*contents))
transactions_count = len(transactions)

# Предварительно получим данные о курсах валют
conversion_rates = {}
for currency in contents[CURRENCY_IDX]:
    response = requests.get(f"https://api.exchangerate.host/convert?from={currency}&to=RUB", timeout=10).json()
    conversion_rates[currency] = response["result"]

# Рассчитаем сумму транзакций (в рублях)
total = sum(
    amount * conversion_rates[currency] for currency, amount in zip(contents[CURRENCY_IDX], contents[AMOUNT_IDX])
)

# Обработаем имена и фамилии клиентов
for idx in range(transactions_count):
    # Если элемент не представляет из себя фамилию, имя и отчество, то никак не изменяем его
    if transactions[idx][CLIENTS_IDX].find(" ") != 2:
        continue
    # Иначе трансформируем согласно правилу
    name, last_name, middle_name = transactions[idx][CLIENTS_IDX].split()
    if len(last_name) > 8:
        transactions[idx][CLIENTS_IDX] = f"{last_name} {name[0]}.{middle_name[0]}."

# Подключение к базе данных
conn = psycopg2.connect(dbname=db_name, user=db_user, password=db_password, host=db_host, port=db_port)
cur = conn.cursor()

# Занесем в базу данных информацию о всех клиентах
for client in contents[CLIENTS_IDX]:
    cur.execute('INSERT INTO "public.Client" (identifier) VALUES (%s) ON CONFLICT DO NOTHING', (client,))
# Завершим транзакцию
conn.commit()

# Занесем в базу данных информацию о всех валютах
for currency in contents[CURRENCY_IDX]:
    cur.execute('INSERT INTO "public.Currency" (code) VALUES (%s) ON CONFLICT DO NOTHING', (currency,))
# Завершим транзакцию
conn.commit()

# Занесем в базу данных информацию о всех транзакциях
for transaction in transactions:
    client, currency, amount = transaction

    cur.execute(
        'INSERT INTO "public.Transaction" (client, currency, amount) VALUES(%s, %s, %s) RETURNING id',
        (client, currency, amount),
    )
    transaction_id = cur.fetchone()[0]

    # Заодно обновим BigTransaction/UsualTransaction
    # BigTransaction — события из списка, сумма транзакций которых больше 1000
    # BigTransaction — события из списка, сумма транзакций которых меньше или равна 1000
    if amount > 1000:
        cur.execute('INSERT INTO "public.BigTransaction" (transaction_id) VALUES(%s)', (transaction_id,))
    else:
        cur.execute('INSERT INTO "public.UsualTransaction" (transaction_id) VALUES(%s)', (transaction_id,))
# Завершим транзакцию
conn.commit()
