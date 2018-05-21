# -*- coding: utf-8 -*-
"""
Модуль для констант серверной части.
"""
import os

current_path = os.path.abspath(__file__)
current_path_tokens = current_path.split('\\')

# Since we have two folders with the same name, pos will get the outer directory index
DEBUG = False
if DEBUG:
    shift = 2
else:
    shift = 1

pos = current_path_tokens.index('NCryptoServer')
DB_PATH = '\\'.join(current_path_tokens[0:(pos + shift)]) + '\\Database\\ServerDB.db'

