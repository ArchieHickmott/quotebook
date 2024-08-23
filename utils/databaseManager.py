class DatabaseManager:
    def __init__(self):
        import sqlite3
        
        self.conn = sqlite3.connect('database.db', check_same_thread=False)

    def query(self, query, values=None):
        '''
        Execute a query on the database.
        :param query: The query to execute.
        :param values: The values to insert into the query.
        '''
        if query.lower().startswith('select'):
            return self.select(query, values)
        else:
            return self.execute(query, values)
        
    def select(self, query, values=None):
        '''
        Execute a select query on the database.
        :param query: The query to execute.
        :param values: The values to insert into the query.
        '''
        with self.conn:
            cursor = self.conn.cursor()

            try:
                cursor.execute(query, values)
                return cursor.fetchall()
            except:
                return False
        
    def execute(self, query, values=None):
        '''
        Execute a query on the database.
        :param query: The query to execute.
        :param values: The values to insert into the query.
        '''
        with self.conn:
            cursor = self.conn.cursor()
            try:
                cursor.execute(query, values)
                cursor.connection.commit()
                return True
            except:
                return False
            
    def reset_db(self):
        '''
        Reset the database.
        '''
        with self.conn:
            cursor = self.conn.cursor()
            with open('database_query.sql', 'r') as f:
                cursor.executescript(f.read())