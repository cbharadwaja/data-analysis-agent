class DataAnalyzer:
    def __init__(self, df): self.df = df
    def describe(self) -> dict: return self.df.describe().to_dict()
    def to_records(self) -> list: return self.df.to_dict(orient='records')