import pickle
import sqlite3
from .constants import *
from definitions import *


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
                command = f'{SELECT_COMMAND} {INDEX} FROM {table} DESC;'
                indexes = [a for (a, ) in self._cursor.execute(command).fetchall()]
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
        self.save()

    def create_tables(self):
        self._create_table(TABLE_USERS, [(USER_USERNAME, str),
                                         (USER_PASSWORD, str),
                                         (USER_HEAD1, bytes),
                                         (USER_HEAD2, bytes),
                                         (USER_BODY1, bytes),
                                         (USER_BODY2, bytes)])

    def add_user(self, username, password):
        command = f'''
        {INSERT_COMMAND} users VALUES (?, ?, ?, ?, ?, ?, ?);
        '''
        head1_image = head2_image = pickle.dumps(pygame.surfarray.array3d(pygame.image.load(HEAD_IMAGE)))
        body1_image = body2_image = pickle.dumps(pygame.surfarray.array3d(pygame.image.load(BODY_IMAGE)))
        self._cursor.execute(command, (self._index(TABLE_USERS), username, password,
                                       head1_image, head2_image, body1_image, body2_image))
        self.save()

    def set_skin(self, username: str, *args):
        command = f"""
        {UPDATE_COMMAND} {TABLE_USERS} SET
        {USER_HEAD1} = ?,
        {USER_HEAD2} = ?,
        {USER_BODY1} = ?,
        {USER_BODY2} = ?
         WHERE {USER_USERNAME} = ?;
        """
        new_args: List[Any] = [pickle.dumps(a) for a in args]
        new_args.append(username)
        self._cursor.execute(command, new_args)
        self.save()

    def get_skin(self, username):
        command = f"""
        {SELECT_COMMAND} {USER_HEAD1}, {USER_HEAD2}, {USER_BODY1}, {USER_BODY2}
         FROM {TABLE_USERS}
         WHERE {USER_USERNAME}=?;
        """
        return [pickle.loads(skin) for skin in self._cursor.execute(command, [username]).fetchone()]

    def save(self):
        self._connection.commit()

    def close(self):
        self.save()
        self._connection.close()

    def _index(self, table):
        index = self._table_ids[table]
        self._table_ids[table] += 1
        return index

    def user_id(self, username):
        command = f"""
        {SELECT_COMMAND} {INDEX} FROM {TABLE_USERS} WHERE {USER_USERNAME} = ?;
        """
        try:
            index, = self._cursor.execute(command, [username]).fetchone()
        except TypeError:
            index = -1
        return index

    @property
    def users_password(self):
        command = f"""
        {SELECT_COMMAND} {USER_PASSWORD} FROM {TABLE_USERS} ORDER BY {INDEX};
        """
        return [password for password, in self._cursor.execute(command).fetchall()]


db = Database()
