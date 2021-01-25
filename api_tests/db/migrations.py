from playhouse.migrate import *
from .connection import db

migrator = PostgresqlMigrator(db)

def run_migrations():
    if not _exist_in_table('sanbase_gql_host', 'gqltestsuite'):
        migrate(migrator.add_column('gqltestsuite', 'sanbase_gql_host', CharField(default='')))

    if not _exist_in_table('_query_url', 'gqltestcase'):
        migrate(migrator.add_column('gqltestcase', '_query_url', TextField(default='')))

def _exist_in_table(field, table):
    return field in list(map(lambda x: x.name, db.get_columns(table)))

if __name__ == "__main__":
    run_migrations()