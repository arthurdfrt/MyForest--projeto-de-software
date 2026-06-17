import sqlite3

class Database:
    def buscar(self, query, params=()):
        conn = sqlite3.connect('database.db')
        result = conn.cursor().execute(query, params).fetchall()
        conn.close()
        return result

    def buscar_um(self, query, params=()):
        conn = sqlite3.connect('database.db')
        result = conn.cursor().execute(query, params).fetchone()
        conn.close()
        return result

    def executar(self, query, params=()):
        conn = sqlite3.connect('database.db')
        conn.cursor().execute(query, params)
        conn.commit()
        conn.close()


class DatabaseProxy:
    def __init__(self):
        self._db = Database()

    def buscar(self, query, params=()):
        print(f"[LOG] SELECT: {query[:60]}")
        return self._db.buscar(query, params)

    def buscar_um(self, query, params=()):
        print(f"[LOG] SELECT ONE: {query[:60]}")
        return self._db.buscar_um(query, params)

    def executar(self, query, params=()):
        print(f"[LOG] EXECUTE: {query[:60]}")
        return self._db.executar(query, params)


db = DatabaseProxy()