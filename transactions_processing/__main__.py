# pylint: disable=import-error

from transactions_processing.config import db_host, db_name, db_password, db_port, db_user
from transactions_processing.database import get_connection, store_clients, store_currencies, store_transactions
from transactions_processing.transactions import retrieve_transactions

clients, currencies, transactions = retrieve_transactions("data/clients.csv", "data/currency.csv", "data/amount.csv")
connection = get_connection(db_name, db_user, db_password, db_host, db_port)

store_clients(connection, clients)
store_currencies(connection, currencies)
store_transactions(connection, transactions)
