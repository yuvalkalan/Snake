import sqlite3

T_NONE = 'NULL'
T_INT = 'INTEGER'
T_FLOAT = 'REAL'
T_STR = 'TEXT'
T_BYTES = 'BLOB'

TYPES = {None: T_NONE,
         int: T_INT,
         float: T_FLOAT,
         str: T_STR,
         bytes: T_BYTES}

CREATE_TABLE_COMMAND = '''CREATE TABLE IF NOT EXISTS'''
INSERT_COMMAND = '''INSERT INTO'''
SELECT_COMMAND = '''SELECT'''

TABLE_USERS = 'users'

INDEX = 'id'

USER_USERNAME = 'username'
USER_PASSWORD = 'password'


class Database:
    def __init__(self):
        self._connection = sqlite3.connect('database.db')
        self._cursor = self._connection.cursor()
        self._table_ids = {}
        self.create_tables()
        self._set_tables_id()

    def _set_tables_id(self):
        tables_command = '''SELECT name FROM sqlite_schema WHERE type ='table' AND name NOT LIKE 'sqlite_%';'''
        tables = self._cursor.execute(tables_command).fetchall()
        for (table,) in tables:
            try:
                indexes = [a for (a, ) in self._cursor.execute(f'{SELECT_COMMAND} id FROM {table} DESC').fetchall()]
                index = max(indexes) + 1
            except ValueError:
                index = 0
            self._table_ids[table] = index

    def _create_table(self, table_name, parameters):
        values = [f'{v} {TYPES[t]}' for v, t in parameters]
        values_str = ',\n'.join(values)
        command = f'''
        {CREATE_TABLE_COMMAND} {table_name}(
            {INDEX} {TYPES[int]} PRIMARY KEY UNIQUE,
            {values_str}
        );
        '''
        self._cursor.execute(command)

    def create_tables(self):
        self._create_table(TABLE_USERS, [(USER_USERNAME, str),
                                         (USER_PASSWORD, str)])
        self._create_table('blabla', [('userssler', str)])

    def add_user(self, username, password):
        command = f'''
        {INSERT_COMMAND} users VALUES (?, ?, ?) 
        '''
        self._cursor.execute(command, (self._index(TABLE_USERS), username, password))

    def save(self):
        self._connection.commit()

    def close(self):
        self.save()
        self._connection.close()

    def _index(self, table):
        index = self._table_ids[table]
        self._table_ids[table] += 1
        return index


def main():
    db = Database()
    db.create_tables()
    for i in range(10):
        db.add_user('yuval', 'kalan')
    db.close()


if __name__ == '__main__':
    main()
