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
UPDATE_COMMAND = '''UPDATE'''

TABLE_USERS = 'users'

INDEX = 'id'

USER_USERNAME = 'username'
USER_PASSWORD = 'password'
USER_HEAD1 = 'head1'
USER_HEAD2 = 'head2'
USER_BODY1 = 'body1'
USER_BODY2 = 'body2'

HEAD_IMAGE = r'files\animation\head.png'
BODY_IMAGE = r'files\animation\body.png'
