import pandas as pd
from services.database import engine

class SQLExecutor:
    def execute(self, sql: str) -> pd.DataFrame:
        return pd.read_sql_query(sql, engine)