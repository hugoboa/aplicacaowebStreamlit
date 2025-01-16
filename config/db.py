import json
import mysql.connector
import psycopg2
from pymongo import MongoClient


def load_config(config_path="config.json"):
    """
    Carrega as configurações do arquivo JSON.
    """
    with open(config_path, "r") as file:
        config = json.load(file)
    return config


def get_mysql_connection(config_path="config.json"):
    """
    Retorna uma conexão com o banco de dados MySQL usando as configurações do arquivo JSON.
    """
    config = load_config(config_path)
    mysql_config = config["mysql"]

    try:
        connection = mysql.connector.connect(
            host=mysql_config["host"],
            user=mysql_config["user"],
            password=mysql_config["password"],
            database=mysql_config["database"],
            port=mysql_config["port"],
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao MySQL: {err}")
        raise


def get_postgresql_connection(config_path="config.json"):
    """
    Retorna uma conexão com o banco de dados PostgreSQL usando as configurações do arquivo JSON.
    """
    config = load_config(config_path)
    postgres_config = config["postgresql"]

    try:
        connection = psycopg2.connect(
            host=postgres_config["host"],
            user=postgres_config["user"],
            password=postgres_config["password"],
            database=postgres_config["database"],
            port=postgres_config["port"],
        )
        return connection
    except psycopg2.Error as err:
        print(f"Erro ao conectar ao PostgreSQL: {err}")
        raise


def get_mongodb_connection(config_path="config.json"):
    """
    Retorna uma conexão com o MongoDB usando as configurações do arquivo JSON.
    """
    config = load_config(config_path)
    mongo_config = config["mongodb"]

    try:
        client = MongoClient(
            host=mongo_config["host"],
            port=mongo_config["port"],
        )
        db = client[mongo_config["database"]]
        return db
    except Exception as err:
        print(f"Erro ao conectar ao MongoDB: {err}")
        raise
