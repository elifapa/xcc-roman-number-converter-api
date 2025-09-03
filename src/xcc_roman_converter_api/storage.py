import os
import psycopg
from psycopg.rows import dict_row
from contextlib import contextmanager

class PostgresStorage:
    def __init__(self, 
                 host: str = os.getenv("DB_HOST", 'localhost'), 
                 port: int = os.getenv("DB_PORT", 5432), 
                 db: str = os.getenv("DB_DB", 'postgres'),
                 user: str = os.getenv("DB_USER", 'admin'),
                 pwd: str = os.getenv("DB_PASSWORD", 'password')):
        self.conn_params = {
            'host': host,
            'port': int(port),
            'dbname': db,
            'user': user,
            'password': pwd
        }

    @contextmanager
    def get_connection(self):
        conn = None
        try:
            conn = psycopg.connect(**self.conn_params)
            yield conn
        finally:
            if conn:
                conn.close()

    def get_all(self, schema:str, table: str, limit: int | None = None):
        """
        Fetch all rows from the specified table, limited by the given number.

        Args:
            table (str): Name of the table.
            limit (int | None): Maximum number of rows to fetch.

        Returns:
            list[dict]: List of rows as dictionaries.
        """
        with self.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                sql = f"SELECT * FROM {schema}.{table}"
                if limit:
                    sql += f" LIMIT {limit}"
                cursor.execute(sql)
                return cursor.fetchall()

    def get_response(self, where ):
        ...

    def create_table_if_not_exists(self, schema: str, table: str, columns: dict[str, str], add_pk: bool = True):
        """
        Creates a table if it does not exist.

        Args:
            table (str): Name of the table.
            columns (dict[str, str]): Dictionary of column names and their SQL types.
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                columns_definition = ', '.join([f"{col} {col_type}" for col, col_type in columns.items()])
                
                if add_pk:
                    columns_definition = 'id SERIAL PRIMARY KEY, ' + columns_definition

                sqls = [
                f"""CREATE SCHEMA IF NOT EXISTS {schema}""",
                f"""CREATE TABLE IF NOT EXISTS {schema}.{table} (
                    {columns_definition}
                )
                """
                ]
                for sql in sqls:
                    cursor.execute(sql)
            conn.commit()
    
    def insert(self, schema, table, payload):
        with self.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                columns = ', '.join(payload.keys())
                placeholders = ', '.join(['%s'] * len(payload))
                sql = f"INSERT INTO {schema}.{table} ({columns}) VALUES ({placeholders})"
                cursor.execute(sql, tuple(payload.values()))
            conn.commit()

# Global storage instance
storage = PostgresStorage()
print(storage.conn_params)