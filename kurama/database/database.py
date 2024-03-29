import pandas as pd
from sqlalchemy import create_engine, MetaData, text, insert
from kurama.config.environment import DB_URL


# TODO: Implement User IDs for schema/tables
class PostgresDatabase:
    """
    Class for performing natural language operations on a SQL database.
    """

    def __init__(self, uri=DB_URL) -> None:
        self.engine = create_engine(uri)
        self.db_name = self.engine.url.database

    def _build_schema_json_from_table(self, table):
        return {
            "name": f"{table.schema}.{table.name}",
            "columns": [
                {
                    "name": column.name,
                    "type": str(column.type),
                    "primary_key": column.primary_key,
                    "nullable": column.nullable,
                }
                for column in table.columns
            ],
        }

    def _get_schemas(self):
        with self.engine.connect() as connection:
            query = text("SELECT schema_name FROM information_schema.schemata")
            result = connection.execute(query)
            # Fetch non-default schemas (including `public`)
            schema_names = [
                row[0]
                for row in result
                if row[0] not in ["information_schema", "pg_catalog", "pg_toast"]
            ]
        return schema_names

    def _get_tables(self, schema_name):
        metadata = MetaData()
        metadata.reflect(bind=self.engine, schema=schema_name)
        return [table for table in metadata.sorted_tables]

    def _get_table_names(self):
        return [table.name for table in self._get_tables()]

    ### Public Methods

    def get_table_schemas(self, schema_name):
        """
        Retrieves a list of table schemas in JSON format from a list of table names.
        """
        return [
            self._build_schema_json_from_table(table)
            for table in self._get_tables(schema_name=schema_name)
        ]

    def get_table_by_name(self, table_name, schema_name):
        """
        Retrieve a SQLAlchemy Table object by the table_name.
        """
        metadata = MetaData()
        metadata.reflect(bind=self.engine, schema=schema_name)
        table = metadata.tables.get(table_name)
        return table

    def get_table_schema_by_name(self, table_name, schema_name):
        table = self.get_table_by_name(table_name=table_name, schema_name=schema_name)
        return self._build_schema_json_from_table(table=table)

    def get_documents_for_user(self, user_id) -> list[str]:
        with self.engine.connect() as connection:
            query = text("SELECT * FROM documents WHERE user_id = :user_id").bindparams(
                user_id=user_id
            )
            result = connection.execute(query)
            connection.commit()
            rows = result.fetchall()
            return rows

    def create_schema_for_user_if_not_exists(self, schema_name) -> None:
        with self.engine.connect() as connection:
            query = text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
            connection.execute(query)
            connection.commit()

    def create_table(self, sql):
        with self.engine.connect() as connection:
            connection.execute(text(sql))
            connection.commit()

    def insert_into(self, table, args):
        with self.engine.connect() as connection:
            stmt = insert(table).values(args)
            connection.execute(stmt)
            connection.commit()

    def execute(self, query):
        """
        This method should only be used for read-only queries
        """
        with self.engine.connect() as connection:
            result = connection.execute(text(query))
            connection.commit()
            rows = result.fetchall()
            columns = result.keys()
            df = pd.DataFrame(rows, columns=columns)
            return df

    def drop_table(self, table_name):
        with self.engine.connect() as connection:
            query = text(f"DROP TABLE {table_name}")
            connection.execute(query)
            connection.commit()
