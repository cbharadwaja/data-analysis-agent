import pandas as pd
from io import StringIO
from services.database import SessionLocal
from models.raw_data import RawData

class DataLoader:
    def __init__(self, content: bytes, filename: str):
        self.text = content.decode('utf-8')
        self.filename = filename

    def load(self) -> pd.DataFrame:
        # Persist raw upload
        with SessionLocal() as db:
            db.add(RawData(filename=self.filename, content=self.text))
            db.commit()
        # Parse
        if self.filename.lower().endswith('.csv'):
            return pd.read_csv(StringIO(self.text))
        if self.filename.lower().endswith('.json'):
            return pd.read_json(StringIO(self.text))
        raise ValueError(f"Unsupported file format: {self.filename}")