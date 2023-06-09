# pylint: disable=import-error

import psycopg2


def get_connection(db_name: str, db_user: str, db_password: str, db_host: str, db_port: str) -> None:
    # Подключение к базе данных
    conn = psycopg2.connect(
        dbname=db_name, user=db_user, password=db_password, host=db_host, port=db_port, connect_timeout=10
    )
    return conn


def store_clients(conn: "psycopg2.connection", clients: list[str]) -> None:
    with conn:
        cur = conn.cursor()
        # Занесем в базу данных информацию о всех клиентах
        for client in clients:
            cur.execute('INSERT INTO "public.Client" (identifier) VALUES (%s) ON CONFLICT DO NOTHING', (client,))


def store_currencies(conn: "psycopg2.connection", currencies: list[str]) -> None:
    with conn:
        cur = conn.cursor()
        # Занесем в базу данных информацию о всех валютах
        for currency in currencies:
            cur.execute('INSERT INTO "public.Currency" (code) VALUES (%s) ON CONFLICT DO NOTHING', (currency,))


def store_transactions(conn: "psycopg2.connection", transactions: list) -> None:
    with conn:
        cur = conn.cursor()
        # Занесем в базу данных информацию о всех транзакциях
        for transaction in transactions:
            client, currency, amount, ruble_amount = transaction

            cur.execute(
                'INSERT INTO "public.Transaction" (client, currency, amount, ruble_amount) VALUES(%s, %s, %s, %s) RETURNING id',
                (client, currency, amount, ruble_amount),
            )
            transaction_id = cur.fetchone()[0]

            # Заодно обновим BigTransaction/UsualTransaction
            # BigTransaction — события из списка, сумма транзакций которых больше 1000
            # UsualTransaction — события из списка, сумма транзакций которых меньше или равна 1000
            if ruble_amount > 1000:
                cur.execute('INSERT INTO "public.BigTransaction" (transaction_id) VALUES(%s)', (transaction_id,))
            else:
                cur.execute('INSERT INTO "public.UsualTransaction" (transaction_id) VALUES(%s)', (transaction_id,))
