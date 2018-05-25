# -*- coding: utf-8 -*-
"""
Модуль, который отвечает за реализацию класса потока-получателя сообщений.
"""
import time
from threading import Thread
from queue import Queue

from NCryptoTools.jim.jim_constants import JIMMsgType
from NCryptoTools.jim.jim_core import JIMMessage
from NCryptoTools.tools.utilities import get_current_time

from NCryptoServer.server_instance_holder import server_holder


class Receiver(Thread):
    """
    Класс потока для приёма сообщений от клиента.
    """
    def __init__(self, client_info, shared_socket, wait_time=0.05, buffer_size=30):
        """
        Конструктор. Атрибут _input_buffer_queue реализован в виде очереди,
        в которой хранятся JSON-объекты (сообщения) от клиента.
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
        self._input_buffer_queue = Queue(buffer_size)
        self._main_window = server_holder.get_instance('MainWindow')
        self._client_manager = server_holder.get_instance('ClientManager')

    def get_msg_from_queue(self):
        """
        Берёт данные из очереди.
        @return: JSON-объект (сообщение).
        """
        return self._input_buffer_queue.get() if self._input_buffer_queue.qsize() > 0 else None

    def run(self):
        """
        Запускает процесс выполнения потока.
        @return: -
        """
        while self._client_info.is_connected():
            try:
                msg_bytes = self._socket.recv(1024)
            except OSError:
                # If user has exited with a TO_SERVER_QUIT message - he quited safely
                if self._client_info.is_safe_quit() is False:
                    login = self._client_info.get_login()
                    ip = self._client_info.get_ip()

                    # Deletes client from the list of clients
                    self._main_window.remove_data_from_tab('Clients', '{} ({})'.format(login, ip))

                    # Shows message that client has closed his connection
                    self._main_window.add_data_in_tab('Log', '[{}] Client {} ({}) has timed out.'.
                                                      format(get_current_time(), login, ip))

                    # Deletes client from the client manager
                    self._client_manager.delete_client('ip', ip)

                    # Triggers threads to quit their routines
                    self._client_info.set_connection_state(False)
            else:
                msg_dict = JIMMessage(JIMMsgType.UNDEFINED_TYPE, 'urf-8', msg_bytes).deserialize()
                self._input_buffer_queue.put(msg_dict)

            time.sleep(self._wait_time)
