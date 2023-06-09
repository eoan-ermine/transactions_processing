# pylint: disable=import-error

import csv
import itertools

import requests


def retrieve_contents(filename: str) -> list[str]:
    with open(filename, encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        # В каждой строке есть как минимум один элемент, поэтому все безопасно
        return list(set(row[0] for row in reader))


def retrieve_conversion_rates(currencies: list[str]) -> dict[str, float]:
    # Предварительно получим данные о курсах валют
    return {
        currency: requests.get(
            f"https://api.exchangerate.host/convert?from={currency}&to=RUB", timeout=10
        ).json()["result"]
        for currency in currencies
    }


def normalize_clients(clients: list[str]) -> None:
    for idx, client in enumerate(clients):
        # Если элемент не представляет из себя фамилию, имя и отчество, то никак не изменяем его
        # В строке должно быть как минимум 5 символов (имя, фамилия, отчество, разделяющие пробелы)
        if len(client) < 5 or client.find(" ") != 2:
            continue
        # Иначе трансформируем согласно правилу
        last_name, name, middle_name = client.split()
        if len(last_name) > 8:
            clients[idx] = f"{last_name} {name[0]}.{middle_name[0]}."


def retrieve_transactions(
    clients_filename: str, currency_filename: str, amount_filename: str
) -> tuple[list[str], list[str], list[tuple[str, str, float, float]]]:
    contents = [retrieve_contents(filename) for filename in (clients_filename, currency_filename, amount_filename)]
    clients_idx, currencies_idx, amounts_idx = 0, 1, 2

    conversion_rates = retrieve_conversion_rates(contents[currencies_idx])

    # Нормализуем идентификаторы всех клиентов
    normalize_clients(contents[clients_idx])
    # Преобразуем все элементы amount в числовые значения
    contents[amounts_idx] = [float(amount) for amount in contents[amounts_idx]]
    # Формируем все уникальные варианты сочетаний переменных из всех файлов + сумма, переведенная в рубли
    transactions = list(itertools.product(*contents))
    # Добавим в каждую информацию о том, сколько это в рублях
    for idx, transaction in enumerate(transactions):
        currency, amount = transaction[currencies_idx], transaction[amounts_idx]
        transactions[idx] = (*transactions[idx], amount * conversion_rates[currency])

    return (contents[clients_idx], contents[currencies_idx], transactions)
