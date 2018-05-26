# -*- coding: utf-8 -*-
"""
Модуль, который отвечает за реализацию класса потока-отправителя сообщений.
"""
import time
from threading import Thread
from queue import Queue

from NCryptoServer.server_instance_holder import server_holder

from NCryptoTools.jim.jim_core import JIMMessage
from NCryptoTools.jim.jim_constants import JIMMsgType


class Sender(Thread):
    """
    Класс потока для отправки сообщений клиенту из буфера для исходящих сообщений.
    """
    def __init__(self, client_info, shared_socket, wait_time=0.05, buffer_size=30):
        """
        Конструктор. Атрибут _output_buffer_queue реализован в виде очереди,
        в которой хранятся JSON-объекты (сообщения) для конкретного клиента.
        @param client_info: ссылка на класс с информацией о пользователе.
        @param shared_socket: клиентский сокет.
        @param wait_time: время ожидания между итерациями. (sec)
        @param buffer_size: размер буфера очереди в количестве элементов.
        """
        super().__init__()
        self.daemon = True
        self._client_info = client_info
        self._socket = shared_socket
        self._wait_time = wait_time
        self._output_buffer_queue = Queue(buffer_size)
        self._client_manager = server_holder.get_instance('ClientManager')

    def add_msg_to_queue(self, recipient_login, msg_bytes):
        """
        Adds new message to the outgoing queue.
        @param recipient_login: login of recipient who receives bytes.
        @param msg_bytes: serialized JSON message (bytes).
        @return: None.
        """
        self._output_buffer_queue.put((recipient_login, msg_bytes))

    def run(self):
        """
        Runs Sender thread.
        @return: None.
        """
        while self._client_info.is_connected():
            if self._output_buffer_queue.qsize() > 0:
                (recipient_login, msg_bytes) = self._output_buffer_queue.get()
                client = self._client_manager.find_client('login', recipient_login)
                if client:
                    try:
                        client.get_socket().send(msg_bytes)
                    except OSError:
                        self._handle_sending_failure(client.get_login(), 'Client {} ({}) has timed out.'.
                                                     format(client.get_login(), client.get_ip()))
            time.sleep(self._wait_time)

    def _handle_sending_failure(self, recipient_login, log_message):
        """
        Данная функция обрабатывает ситуацию, когда было получено исключение при отправке
        сообщения пользователю. Она делает следующее:
        - удаляет пользователя из списка во вкладке Clients;
        - добавляет сообщение во вкладку Log, что пользователь ушёл в Offline;
        - отсылает сообщения всем контактам пользователя, что данный клиент ушёл в Offline.
        @param recipient_login: логин пользователя, которому не удалось переслать сообщение.
        @param log_message: строка с сообщением для вкладки Log.
        @return: -
        """
        main_window = server_holder.get_instance('MainWindow')

        # Удаление пользователя со вкладки Clients - он больше не среди Online клиентов
        main_window.remove_data_from_tab('Clients', recipient_login)

        # Добавление сообщения в лог об уходе пользователя в Offline
        main_window.add_data_in_tab('Log', log_message)

        msg_time_out = JIMMessage(JIMMsgType.CTS_QUIT, action='quit')
        all_contacts = server_holder.get_instance('ServerStorage').get_overall_client_contacts(recipient_login)

        # Удаление пользователя из списка
        self._client_manager.delete_client(recipient_login)

        if all_contacts:
            for login in all_contacts:
                self.add_msg_to_queue(login, msg_time_out)
