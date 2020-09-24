from playhouse.migrate import *
from .connection import db

migrator = PostgresqlMigrator(db)

def run_migrations():
    migrate(migrator.add_column('gqltestsuite', 'sanbase_gql_host', CharField(default='')))

if __name__ == "__main__":
    run_migrations()