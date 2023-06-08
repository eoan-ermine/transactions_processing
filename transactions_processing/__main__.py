import csv
import itertools

import requests

source_files = ["clients.csv", "currency.csv", "amount.csv"]
contents = []
CLIENTS_IDX, CURRENCY_IDX, AMOUNT_IDX = 0, 1, 2

for source_file in source_files:
    # Наиболее эффективное решение: предварительно создать set и пополнять его вручную
    # Если мы напишем что-то вроде set([value for value in values]), то у нас будут лишние расходы
    # на формирование списка
    values = set()
    with open(f"../data/{source_file}", encoding="utf-8") as csvfile:
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
