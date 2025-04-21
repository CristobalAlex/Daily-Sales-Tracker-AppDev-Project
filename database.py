import mariadb
# ito sa mga functions like yang execute query
class Database:
    def __init__(self, config):
        self.config = config
        self.conn = None
        self.cursor = None

    def connect(self):
        if self.conn is None:
            self.conn = mariadb.connect(**self.config)
            self.cursor = self.conn.cursor(dictionary=True)

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def execute_query(self, query, params=None):
        try:
            self.connect()  # Ensure the connection is active
            self.cursor.execute(query, params or ())
            result = self.cursor.fetchall()
            return result
        except mariadb.Error as e:
            print(f"Error executing query: {e}")
            return None

    def execute_non_query(self, query, params=None):
        try:
            self.connect()  # Ensure the connection is active
            self.cursor.execute(query, params or ())
            self.conn.commit()
            return True
        except mariadb.Error as e:
            print(f"Error executing non-query: {e}")
            return False
    