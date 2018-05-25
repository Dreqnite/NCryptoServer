# -*- coding: utf-8 -*-
"""
Модуль для реализации потока, принимающего новые запросы на соединения от клиентов.
"""
import time
import socket
import datetime
from threading import Thread

from NCryptoTools.tools.utilities import get_formatted_date

from NCryptoServer.server_instance_holder import server_holder


class ConnectionAcceptor(Thread):
    """
    Данный класс занимается вопросами принятия новых соединений от клиентов.
    """
    def __init__(self,
                 ipv4_address='localhost',
                 port_number='7777',
                 socket_family=socket.AF_INET,
                 socket_type=socket.SOCK_STREAM,
                 wait_time=0.05):
        super().__init__()
        self.daemon = True
        self._socket = socket.socket(socket_family, socket_type)
        self._socket.bind((ipv4_address, int(port_number)))
        self._socket.listen(5)
        self._socket.settimeout(0.2)
        self._wait_time = wait_time
        self._client_manager = server_holder.get_instance('ClientManager')
        self._main_window = server_holder.get_instance('MainWindow')

    def __del__(self):
        """
        Деструктор. Закрывает слушающий сокет при удалении объекта.
        @return: -
        """
        self._socket.close()

    def run(self):
        """
        Запускает выполнение потока. Принимает новые соединения.
        @return: -
        """
        while True:
            try:
                # client_addr_info - это кортеж (<address>; <socket number>)
                (client_socket, client_addr_info) = self._socket.accept()
            except OSError:
                pass
            else:
                login = get_new_login()
                connection_time = datetime.datetime.now().timestamp()

                # Добавление клиента в список клиентов с которыми наш сервер работает
                self._client_manager.add_client(client_socket, client_addr_info[0], connection_time, login)

                # Добавление информации о событии во вкладку Log
                self._main_window.add_data_in_tab('Log', '[{}] Connection request from: {} (socket: {}).'.
                                                  format(get_formatted_date(connection_time),
                                                         client_addr_info[0],
                                                         client_addr_info[1]))

            time.sleep(self._wait_time)


def get_new_login():
    """
    Composes string with user name, whose login is unknown.
    Login has such pattern: 'Anonymous#', where # - UNIX-time in ms.
    @return: login for anonymous user.
    """
    unix_time = str(datetime.datetime.now().timestamp()).replace('.', '-')
    return 'Anonymous-{}'.format(unix_time)
