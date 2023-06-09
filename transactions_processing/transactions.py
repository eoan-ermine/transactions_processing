# pylint: disable=import-error

import csv
import itertools

import requests

CLIENTS_IDX, CURRENCY_IDX, AMOUNT_IDX = 0, 1, 2


def retrieve_contents(filename: str) -> list[str]:
    # Наиболее эффективное решение: предварительно создать set и пополнять его вручную
    # Если мы напишем что-то вроде set([value for value in values]), то у нас будут лишние расходы
    # на формирование списка
    values = set()
    with open(filename, encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            # В каждой строке есть как минимум один элемент, поэтому все безопасно
            values.add(row[0])
    return list(values)


def retrieve_conversion_rates(currencies: list[str]) -> dict[str, float]:
    # Предварительно получим данные о курсах валют
    conversion_rates = {}
    for currency in currencies:
        response = requests.get(f"https://api.exchangerate.host/convert?from={currency}&to=RUB", timeout=10).json()
        conversion_rates[currency] = response["result"]
    return conversion_rates


def normalize_clients(clients: list[str]) -> None:
    for idx, client in enumerate(clients):
        # Если элемент не представляет из себя фамилию, имя и отчество, то никак не изменяем его
        if client.find(" ") != 2:
            continue
        # Иначе трансформируем согласно правилу
        name, last_name, middle_name = client.split()
        if len(last_name) > 8:
            clients[idx] = f"{last_name} {name[0]}.{middle_name[0]}."


def retrieve_transactions(
    clients_filename: str, currency_filename: str, amount_filename: str
) -> tuple[list[str], list[str], list[tuple[str, str, float, float]]]:
    contents = [retrieve_contents(filename) for filename in (clients_filename, currency_filename, amount_filename)]

    conversion_rates = retrieve_conversion_rates(contents[CURRENCY_IDX])

    # Преобразуем все элементы amount в числовые значения
    normalize_clients(contents[CLIENTS_IDX])
    contents[AMOUNT_IDX] = [float(amount) for amount in contents[AMOUNT_IDX]]
    # Формируем все уникальные варианты сочетаний переменных из всех файлов + сумма, переведенная в рубли
    transactions = list(itertools.product(*contents))
    # Добавим в каждую информацию о том, сколько это в рублях
    for idx, transaction in enumerate(transactions):
        currency, amount = transaction[CURRENCY_IDX], transaction[AMOUNT_IDX]
        transactions[idx] = (*transactions[idx], amount * conversion_rates[currency])

    return (contents[CLIENTS_IDX], contents[CURRENCY_IDX], transactions)
