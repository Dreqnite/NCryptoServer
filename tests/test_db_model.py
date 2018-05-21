# -*- coding: utf-8 -*-
"""
Testing module for database.
"""
import pytest
from Solution.NCryptoServer.Database.db_model import get_current_max_id
# import sqlite3
# from Solution.ServerApp.Utils.constants import *
# from Solution.ServerApp.Database.db_model import Client, \
#                                                  session


@pytest.mark.parametrize('table_name, expected', [
    ('client', True),
    ('client_contacts', True),
    ('chatroom', True),
    ('chatroom_client', True),
    ('message', False)
])
def test_get_current_max_id(table_name, expected):
    """
    Tests function get_current_max_id() from the server_storage.py.
    Function returs the MAX value of the PK.
    @param table_name: table name (not ORM classes!) .
    @param expected: expected value (boolean).
    @return: -
    """
    result = get_current_max_id(table_name)
    assert expected == isinstance(result, int)

# class SQLiteConnection:
#     def __init__(self, db_file_path):
#         self._connection = sqlite3.connect(db_file_path)
#         self._cursor = self._connection.cursor()
#
#     def select_all_entries_from_table(self, table_name):
#         """
#         Gets all entries from the needed table.
#         @param table_name: table name (not ORM classes!) .
#         @return: -
#         """
#         self._cursor.execute('SELECT * FROM {};'.format(table_name))
#
#         rows = self._cursor.fetchall()
#
#         self.select_rows_names_from_table()
#
#         for row in rows:
#             print(row)
#         print('-' * 79)
#         print('Total rows fetched: {}'.format(len(rows)))
#         print('-' * 79)
#
#     def select_rows_names_from_table(self):
#         """
#         Gets rows names from the cursor.
#         @return: -
#         """
#         table_header = ''
#         for description in self._cursor.description:
#             table_header += '| {} '.format(description[0])
#         table_header += '|'
#
#         print('-' * len(table_header))
#         print(table_header)
#         print('-' * len(table_header))
#
#     def select_clients_in_chatroom(self, chatroom_name):
#         self._cursor.execute('SELECT * FROM {};'.format(chatroom_name))
#
#
# def main():
#     try:
#         connection = SQLiteConnection(DB_PATH)
#     except OSError as e:
#         print(str(e))
#     else:
#         connection.select_all_entries_from_table('client')
#         connection.select_all_entries_from_table('client_contacts')
#         connection.select_all_entries_from_table('chatroom')
#         connection.select_all_entries_from_table('chatroom_client')
#
#         # names = [description[0] for description in cursor.description]
#         # connection.select_all_entries_from_table('table')
#
#
# if __name__ == '__main__':
#     main()
