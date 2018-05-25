# -*- coding: utf-8 -*-
"""
Модуль для констант серверной части.
"""
import os

current_path = os.path.abspath(__file__)
current_path_tokens = current_path.split('\\')

DEBUG = True
if DEBUG:
    shift = 2
else:
    shift = 1

pos = current_path_tokens.index('NCryptoServer')
DATABASE_PATH = '\\'.join(current_path_tokens[0:(pos + shift)]) + '\\db\\NCryptoDatabase.db'
