# -*- coding: utf-8 -*-
"""
Модуль, который предназначен для определения классов и функций, связанных с их
основной информацией.
"""
from NCryptoServer.net.client_connection import ClientHandler


class ClientManager:
    """
    Класс, предназначенный для хранения информации о клиентах. Другие модули могут
    обращаться сюда за получением сокетов, IP-адресов и логинов.
    """
    def __init__(self):
        self._clients = []

    def add_client(self, client_socket, ip_address, connection_time, login):
        """
        Добавляет нового клиента в список клиентов.
        @param client_socket: сокет клиента.
        @param ip_address: IP-адрес клиента.
        @param connection_time: временная отметка UNIX, когда клиент присоеденился
        к серверу.
        @param login: логин клиента.
        @return: -
        """
        self._clients.append(Client(client_socket, ip_address, connection_time, login))

    def delete_client(self, attribute, value):
        """
        Удаляет клиента с заданными атрибутами из списка клиентов.
        @param attribute: атрибут для поиска.
        @param value: значение атрибута.
        @return: -
        """
        client = self.find_client(attribute, value)
        if client is None:
            return
        self._clients.remove(client)
        del client

    def find_client(self, attribute, value):
        """
        Осуществляет поиск по определённому атрибуту клиента, коими
        могут являться: сокет, Ip и логин пользователя.
        @param attribute: атрибут для поиска.
        @param value: значение атрибута.
        @return: экземпляр класса Client с необходимым значением атрибута.
        """
        for client in self._clients:
            # TODO:
            attribute_callables = {'socket': None,
                                   'ip': client.get_ip,
                                   'login': client.get_login}
            if attribute_callables[attribute]() == value:
                return client
        return None


class Client:
    """
    Данный класс хранит всю информацию о конкретном клиенте, которая необходима
    серверу для поддержки соединения. Для каждого сокета клиента создаётся отдельный
    обработчик.
    """
    def __init__(self, client_socket, ip_address, connection_time, login):
        """
        Конструктор. Если пользователь не захотел авторизоваться то его логин будет
        пустым, то есть None.
        @param client_socket: сокет клиента.
        @param ip_address: IP-адрес клиента.
        @param connection_time: временная отметка UNIX, когда клиент присоеденился
        к серверу.
        @param login: логин клиента, если он авторизован.
        """
        self._is_connected = True
        self._safe_quit = False
        self._ip_address = ip_address
        self._connection_time = connection_time
        self._login = login
        self._handler = ClientHandler(self, client_socket, 0.05)
        self._handler.start()

    def is_connected(self):
        """
        Геттер. Возвращает булевую переменную, которая показывает,
        соединён клиент с сервером или нет.
        @return: булевое значение, которое показывает, соединён клиент с сервером или нет.
        """
        return self._is_connected

    def set_connection_state(self, new_state):
        """
        Сеттер. Устанавливает булевое значение, которое показывает,
        соединён клиент с сервером или нет.
        @param new_state: новое значение соединения с сервером.
        @return: -
        """
        self._is_connected = new_state

    def get_socket(self):
        """
        Геттер. Возвращает сокет клиента.
        @return: сокет клиента.
        """
        return self._handler.get_socket()

    def get_ip(self):
        """
        Геттер. Возвращает IP-адрес клиента.
        @return: IP-адрес клиента.
        """
        return self._ip_address

    def get_login(self):
        """
        Геттер. Возвращает логин клиента.
        @return: логин клиента.
        """
        return self._login

    def set_login(self, login):
        """
        Сеттер. Устанавливает логин анонимного пользователя при авторизации.
        @return: -
        """
        self._login = login

    def is_safe_quit(self):
        return self._safe_quit

    def set_quit_safety(self, new_state):
        self._safe_quit = new_state
