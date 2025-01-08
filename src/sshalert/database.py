import sqlite3
import os


class TableNotMatch(Exception):
    pass


class Database:
    __instance__ = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance__ is None:
            cls.__instance__ = super().__new__(cls)
        return cls.__instance__

    def __init__(self, path="database.db"):
        self.path = path
        self.session = sqlite3.connect(self.path)
        if not os.path.exists(self.path):
            self.create()

    def create(self, force=False) -> bool:
        TABLE_SCHEMA = """CREATE TABLE Data (
            Number INTEGER PRIMARY KEY AUTOINCREMENT,
            Count INTEGER,
            Time TEXT,
            IP TEXT,
            UserName TEXT,
            Way TEXT,
            Password TEXT,
            Version TEXT,
            SessionID TEXT
        )"""

        cursor = self.session.cursor()

        db_exists = os.path.exists(self.path)

        if not force:
            if db_exists:
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='Data'")
                table_exists = cursor.fetchone() is not None

                if not table_exists:
                    cursor.execute(TABLE_SCHEMA)
                    self.session.commit()
                    return True
                else:
                    cursor.execute(
                        "SELECT sql FROM sqlite_master WHERE type='table' AND name='Data'")
                    current_schema = cursor.fetchone()[0]
                    if ' '.join(
                            current_schema.split()) == ' '.join(
                            TABLE_SCHEMA.split()):
                        return True
                    else:
                        raise TableNotMatch()
            else:
                cursor.execute(TABLE_SCHEMA)
                self.session.commit()
                return True
        else:
            if db_exists:
                cursor.execute("DROP TABLE IF EXISTS Data")
                cursor.execute(TABLE_SCHEMA)
                self.session.commit()
                return True
            else:
                cursor.execute(TABLE_SCHEMA)
                self.session.commit()
                return True

