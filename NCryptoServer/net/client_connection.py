# -*- coding: utf-8 -*-
"""
Модуль для общего класса, который агрегирует функции передатчика, прёмника и обработчика.
"""
import time
from threading import Thread

from NCryptoTools.Tools.utilities import get_current_time
from NCryptoTools.JIM.jim import JIMManager
from NCryptoTools.JIM.jim_base import JSONObjectType, UnknownJSONObjectType

from NCryptoServer.server_instance_holder import *
from NCryptoServer.Transmitter.server_sender import Sender
from NCryptoServer.Transmitter.server_receiver import Receiver
from NCryptoServer.Database.server_storage import SQLErrorNotFound, SQLIntegrityError


class ClientHandler(Thread):
    """
    Класс-поток, который агрегирует функции передатчика, приёмника и обработчика.
    В качестве своих атрибутов содержит экземпляры классов-потоков Sender и Receiver,
    которые занимаются отправкой сообщений из буфера и записью приходящих сообщений
    в буфер соответственно. ClientHandler работает с этими буферами и обрабатывает их
    содержимое, сопоставляя каждому типу сообщения определённый вариант поведения.
    """
    def __init__(self, client_info, client_socket, wait_time=0.05):
        """
        Конструктор.
        @param client_info: ссылка на класс, которых хранит основную информацию о клиенте.
        @param client_socket: сокет клиента.
        @param wait_time: время ожидания между итерациями потока. (sec)
        """
        super().__init__()
        self.daemon = True
        self._client_info = client_info
        self._socket = client_socket
        self._wait_time = wait_time

        self._sender = Sender(client_info, self._socket, 0.05, 30)
        self._receiver = Receiver(client_info, self._socket, 0.05, 30)

        self._db_connection = server_holder.get_instance('ServerRepository')
        self._main_window = server_holder.get_instance('MainWindow')

    def __del__(self):
        self._socket.close()

    def run(self):
        """
        Запускает выполнение потока.
        @return: -
        """
        self._sender.start()
        self._receiver.start()

        while self._client_info.is_connected():
            msg_dict = self._receiver.get_msg_from_queue()
            if msg_dict:
                self._handle_message(msg_dict)
            time.sleep(self._wait_time)

    def get_socket(self):
        """
        Возвращает сокет данного клиента.
        @return: сокет клиента.
        """
        return self._socket

    def _handle_message(self, msg_dict):
        """
        Обрабатывает входящие сообщения и выполняет определённые действия в
        зависимости от того, к какому типу сообщение относится.
        @param msg_dict: JSON-объект (сообщение).
        @return: -
        """
        try:
            json_object_type = JIMManager.determine_jim_msg_type(msg_dict)
        except UnknownJSONObjectType:
            return

        # Пользователь пытается пройти авторизацию чата
        if json_object_type == JSONObjectType.TO_SERVER_AUTH:
            self._client_to_server_authenticate(msg_dict)

        # Пользователь решил покинуть чат-приложение (закрыть соединение)
        elif json_object_type == JSONObjectType.TO_SERVER_QUIT:
            self._client_to_server_quit(msg_dict)

        # Пользователь пришёл онлайн
        elif json_object_type == JSONObjectType.TO_SERVER_PRESENCE:
            self._client_to_server_presence(msg_dict)

        # Пользователь пишет другому клиенту в личные сообщения, а не в чат
        elif json_object_type == JSONObjectType.TO_SERVER_PERSONAL_MSG:
            self._client_to_server_personal_msg(msg_dict)

        # Пользователь пишет в чат-комнату
        elif json_object_type == JSONObjectType.TO_SERVER_CHAT_MSG:
            self._client_to_server_chat_msg(msg_dict)

        # Пользователь пытается присоедениться к чат-комнате
        elif json_object_type == JSONObjectType.TO_SERVER_JOIN_CHAT:
            self._client_to_server_join_chat(msg_dict)

        # Пользователь пытается покинуть чат-комнату
        elif json_object_type == JSONObjectType.TO_SERVER_LEAVE_CHAT:
            self._client_to_server_leave_chat(msg_dict)

        # Пользователь пытается получить список его контактов
        elif json_object_type == JSONObjectType.TO_SERVER_GET_CONTACTS:
            self._client_to_server_get_contacts(msg_dict)

        # Пользователь пытается добавить нового пользователя в список контактов
        elif json_object_type == JSONObjectType.TO_SERVER_ADD_CONTACT:
            self._client_to_server_add_contact(msg_dict)

        # Пользователь пытается удалить пользователя из списка контактов
        elif json_object_type == JSONObjectType.TO_SERVER_DEL_CONTACT:
            self._client_to_server_del_contact(msg_dict)

        elif json_object_type == JSONObjectType.TO_SERVER_GET_MSGS:
            self._client_to_server_get_msgs(msg_dict)

    def _send_broadcast(self, recipients_logins, msg_dict):
        """
        Оправляет сообщение списку клиентов.
        @param recipients_logins: список логинов получателей.
        @param msg_dict: JSON-объект (сообщение).
        @return: -
        """
        for login in recipients_logins:
            self._sender.add_msg_to_queue(login, msg_dict)

    # ========================================================================
    # Группа приватных методов, кажый из которых отвечает за обработку сооб-
    # щений определённого типа.
    # ========================================================================
    def _client_to_server_authenticate(self, msg_dict):
        """
        Осуществляет авторизацию пользователя, проверяя его запись в БД.
        @param msg_dict: JSON-объект (сообщение). Структура:
        {'action': self._action,
         'time': self._time,
         'user': {'login': self._login,
                  'password': self._password
                  }
        }
        @return: -
        """
        client_login = msg_dict['user']['login']
        client_password = msg_dict['user']['password']

        authentication_success = self._db_connection.authenticate_client(client_login, client_password)

        # Если аутентификация прошла успешно, то отсылаем соответствующее сообщение-ответ
        if authentication_success is True:
            response_msg = JIMManager.create_jim_object(JSONObjectType.TO_CLIENT_INFO,
                                                        200, 'Authentication is successful!')

            # Добавление сообщения в Log
            self._main_window.add_data_in_tab('Log', '[{}] Client ({}) has logged in as {}.'.
                                              format(get_current_time(),
                                                     self._client_info.get_ip(),
                                                     client_login))

            # Добавление клиента в список клиентов на вкладку Clients
            self._main_window.add_data_in_tab('Clients', '{} ({})'.format(client_login,
                                                                          self._client_info.get_ip()))
            self._client_info.set_login(client_login)

        # В ином случае оповещаем пользователя об ошибке аутентификации
        else:
            # if user failed authentication, we take reserved login ('Anonymous####')
            client_login = self._client_info.get_login()

            response_msg = JIMManager.create_jim_object(JSONObjectType.TO_CLIENT_ERROR,
                                                        401, 'Authentication has failed!')
            self._main_window.add_data_in_tab('Log', '[{}] Client {} has failed authentication.'.
                                              format(get_current_time(),
                                                     self._client_info.get_ip()))

        self._sender.add_msg_to_queue(client_login, response_msg.to_dict())

    def _client_to_server_quit(self, msg_dict):
        """
        Вызов данного метода подразумевает, что пользователь решил отсоедениться от чата,
        например, закрыв программу. В таком случае необходимо оповестить всех пользователей,
        что данный клиент ушёл в оффлайн.
        @param msg_dict: JSON-объект (сообщение). Структура:
        {'action': self._action}
        @return: -
        """
        self._client_info.set_quit_safety(True)

        # Если пользователь не автризовался в чате, то информация, что он покинул чат,
        # остаётся только на сервере - остальным пользователям ничего не отправляем
        client_login = self._client_info.get_login()
        if client_login.startswith('Anonymous') is False:
            client_contacts = self._db_connection.get_overall_client_contacts(client_login)

            if client_contacts:
                self._send_broadcast(client_contacts, msg_dict)

            # Удаление пользователя со вкладки Clients - он больше не среди Online клиентов
            self._main_window.remove_data_from_tab('Clients', '{} ({})'.format(client_login,
                                                                               self._client_info.get_ip()))

        self._client_info.set_connection_state(False)

        # Добавление сообщения в лог об уходе пользователя в Offline
        self._main_window.add_data_in_tab('Log', '[{}] Client {} ({}) has closed the connection.'.
                                          format(get_current_time(),
                                                 client_login,
                                                 self._client_info.get_ip()))
        # Удаление сокета из списка (поиск клиента по логину)
        server_holder.get_instance('ClientManager').delete_client('login', client_login)

    def _client_to_server_presence(self, msg_dict):
        """
        Данный тип сообщений относится только к авторизированным пользователям.
        Клиент оповещает сервер о своём присутствии.
        мессенджер может отправлять prob-запросы клиенту через определённый интервал
        времени, чтобы убедиться, что тот всё ещё online. Клиент в таком случае отве-
        чает presence-сообщением.
        Note: сообщение данного типа может использоватеься только авторизованными
        пользователями.
        @param msg_dict: JSON-объект (сообщение). Структура:
        {'action': self._action,
         'time': self._time,
         'type': self._type,
         'user': {'login': self._login,
                  'status': self._status
                  }
        }
        @return: -
        """
        pass

    def _client_to_server_personal_msg(self, msg_dict):
        """
        Сообщение, которое отправляется другому пользователю в личную переписку.
        Note: сообщение данного типа может использоватеься только авторизованными
        пользователями.
        @param msg_dict: JSON-объект (сообщение). Структура:
        {'action': self._action,
         'time': self._time,
         'to': self._login_to,
         'from': self._login_from,
         'encoding': self._encoding,
         'message': self._message}
        @return: -
        """
        recipinet_login = msg_dict['to']

        # Сообщение должно содержать хотя бы один символ
        error_msg = None
        if len(msg_dict['message']) == 0:
            error_msg = JIMManager.create_jim_object(JSONObjectType.TO_CLIENT_ERROR, 400, 'Message is empty!')

        # Получатель должен быть в БД
        if self._db_connection.client_exists(recipinet_login) is False:
            error_msg = \
                JIMManager.create_jim_object(JSONObjectType.TO_CLIENT_ERROR,
                                             404, 'Client \'{}\' does not exists!'.format(recipinet_login))
        # Получатель должен быть онлайн
        if self._main_window.data_in_tab_exists(
                'Clients', '{} ({})'.format(recipinet_login, self._client_info.get_ip())) is not True:
            error_msg = \
                JIMManager.create_jim_object(JSONObjectType.TO_CLIENT_ERROR,
                                             404, 'Client \'{}\' is not Online!'.format(recipinet_login))

        if error_msg is None:
            # Отправляем сообщение получателю
            self._sender.add_msg_to_queue(recipinet_login, msg_dict)

            # Отправляем ответ отправителю, что сообщение доставлено
            response_msg = JIMManager.create_jim_object(
                JSONObjectType.TO_CLIENT_INFO, 200, 'Message to \'{}\' has been delivered!'.format(recipinet_login))
            self._sender.add_msg_to_queue(msg_dict['from'], response_msg.to_dict())

        # В случае ошибки отправляем сообщение отправителю
        else:
            self._sender.add_msg_to_queue(msg_dict['from'], error_msg.to_dict())

    def _client_to_server_chat_msg(self, msg_dict):
        """
        Осуществляет пересылку сообщения в чат-комнату.
        Note: сообщение данного типа может использоватеься только авторизованными
        пользователями.
        @param msg_dict: JSON-объект (сообщение). Структура:
        {'action': self._action,
         'time': self._time,
         'to': self._login_to,
         'from': self._login_from,
         'message': self._message}
        @return: -
        """
        error_msg = None
        chatroom_name = msg_dict['to']

        # Сообщение должно содержать хотя бы один символ
        if len(msg_dict['message']) == 0:
            error_msg = JIMManager.create_jim_object(JSONObjectType.TO_CLIENT_ERROR, 400, 'Message is empty!')

        # Чат-комната должна быть в БД
        if self._db_connection.chatroom_exists(chatroom_name) is False:
            error_msg = \
                JIMManager.create_jim_object(JSONObjectType.TO_CLIENT_ERROR,
                                             404, 'Chatroom \'{}\' does not exists!'.format(chatroom_name))

        # Получение логинов пользователей, которые являются участиками чат-комнаты
        chatroom_participants = self._db_connection.get_chatroom_clients(chatroom_name)
        if not chatroom_participants:
            error_msg = JIMManager.create_jim_object(JSONObjectType.TO_CLIENT_ERROR,
                                                     404, 'Chatroom is empty!')

        if error_msg is None:
            # Отправляем сообщение в чат-комнату (всем её участникам, кроме отправителя)
            chatroom_participants.remove(msg_dict['from'])
            self._send_broadcast(chatroom_participants, msg_dict)

            # Отправляем ответ отправителю, что сообщение доставлено
            response_msg = JIMManager.create_jim_object(
                JSONObjectType.TO_CLIENT_INFO, 200, 'Message to \'{}\' has been delivered!'.format(chatroom_name))
            self._sender.add_msg_to_queue(msg_dict['from'], response_msg.to_dict())

        # В случае ошибки отправляем сообщение отправителю
        else:
            self._sender.add_msg_to_queue(msg_dict['from'], error_msg.to_dict())

    def _client_to_server_join_chat(self, msg_dict):
        """
        Осуществляет присоединение клиента к списку участников чат-комнаты.
        @param msg_dict: JSON-объект (сообщение). Структура:
        {'action': self._action,
         'time': self._time,
         'login': self._login,
         'room': self._room}
        @return: -
        """
        chatroom_name = msg_dict['room']
        client_login = self._client_info.get_login()

        response_msg = None
        try:
            if self._db_connection.add_client_to_chatroom(client_login, chatroom_name) is False:
                raise SQLIntegrityError('{}, {}'.format(client_login, chatroom_name))

        except SQLErrorNotFound as e:
            response_msg = JIMManager.create_jim_object(JSONObjectType.TO_CLIENT_ERROR, 404, str(e))

        except SQLIntegrityError as e:
            response_msg = JIMManager.create_jim_object(JSONObjectType.TO_CLIENT_ERROR, 403, str(e))

        else:
            response_msg = JIMManager.create_jim_object(JSONObjectType.TO_CLIENT_INFO, 200,
                                                        'You have joined \'{}\' chatroom!'.format(chatroom_name))

            # Оповещение участников чат-комнаты о данном событии
            chatroom_participants = self._db_connection.get_chatroom_clients(chatroom_name)
            if chatroom_participants:
                self._send_broadcast(chatroom_participants, msg_dict)

            # Добавление сообщения в лог об успешном присоединении пользователя к чат-комнате
            self._main_window.add_data_in_tab('Log', '[{}] Client {} ({}) has joined {}.'.format(
                get_current_time(), client_login, self._client_info.get_ip(), chatroom_name))
        finally:
            self._sender.add_msg_to_queue(client_login, response_msg.to_dict())

    def _client_to_server_leave_chat(self, msg_dict):
        """
        Осуществляет удаление клиента из списка участников чат-комнаты.
        @param msg_dict: JSON-объект (сообщение). Структура:
        {'action': self._action,
         'time': self._time,
         'login': self._login,
         'room': self._room}
        @return: -
        """
        chatroom_name = msg_dict['room']
        client_login = self._client_info.get_login()

        response_msg = None
        try:
            if self._db_connection.del_client_from_chatroom(client_login, chatroom_name) is False:
                raise SQLIntegrityError('{}, {}'.format(client_login, chatroom_name))

        except SQLErrorNotFound as e:
            response_msg = JIMManager.create_jim_object(JSONObjectType.TO_CLIENT_ERROR, 404, str(e))

        except SQLIntegrityError as e:
            response_msg = JIMManager.create_jim_object(JSONObjectType.TO_CLIENT_ERROR, 403, str(e))

        else:
            response_msg = JIMManager.create_jim_object(JSONObjectType.TO_CLIENT_INFO, 200,
                                                        'You have left \'{}\' chatroom!'.format(chatroom_name))

            # Оповещение участников чат-комнаты о данном событии
            chatroom_participants = self._db_connection.get_chatroom_clients(chatroom_name)
            if chatroom_participants:
                self._send_broadcast(chatroom_participants, msg_dict)

            # Добавление сообщения в лог об успешном удалении пользователя из чат-комнаты
            self._main_window.add_data_in_tab('Log', '[{}] Client {} ({}) has left {}.'.format(
                get_current_time(), client_login, self._client_info.get_ip(), chatroom_name))
        finally:
            self._sender.add_msg_to_queue(client_login, response_msg.to_dict())

    def _client_to_server_get_contacts(self, msg_dict):
        """
        Осуществляет пересылку клиенту информации о количестве имеющихся у него
        контактов и логинах каждого из контактов.
        @param msg_dict: JSON-объект (сообщение). Структура:
        {'action': self._action,
         'time': self._time}
        @return: -
        """
        client_login = self._client_info.get_login()

        # Добавление сообщения в Log о запросе пользователя списка его контактов
        self._main_window.add_data_in_tab(
            'Log', '[{}] Client {} ({}) requested list of contacts.'.
            format(get_current_time(), client_login, self._client_info.get_ip()))

        # Gets contacts by client login (clients + chatrooms)
        client_contacts = self._db_connection.get_client_contacts(client_login)
        client_contacts.extend(self._db_connection.get_client_chatrooms(client_login))

        # Если у пользователя имеются контакты, то продолжаем
        if client_contacts:
            # Отправляется сообщение с количеством контактов
            msgs_to_send = [JIMManager.create_jim_object(JSONObjectType.TO_CLIENT_QUANTITY,
                                                         202, len(client_contacts))]

            # Отправляется набор сообщений с логинами контактов
            for login in client_contacts:
                contact_msg = JIMManager.create_jim_object(JSONObjectType.TO_CLIENT_CONTACT_LIST, login)
                msgs_to_send.append(contact_msg)

            for msg_to_send in msgs_to_send:
                self._sender.add_msg_to_queue(client_login, msg_to_send.to_dict())

                # Необходимо подгружать с некоторыми промещутками, так как в ином случае
                # передаётся только первый контакт, а все остальные сериализуются неверноб
                # что приводит к ошибке на стороне клиента
                time.sleep(0.1)

        # Если контакты отсутствуют, то оповещаем пользователя об этом
        else:
            response_msg = JIMManager.create_jim_object(JSONObjectType.TO_CLIENT_ERROR,
                                                        404, 'No contacts were found!')
            self._sender.add_msg_to_queue(client_login, response_msg.to_dict())

    def _client_to_server_add_contact(self, msg_dict):
        """
        Осуществляет добавление контакта к пользователю в список контактов.
        @param msg_dict: JSON-объект (сообщение). Структура:
        {'action': self._action,
         'time': self._time,
         'login': self._login}
        @return: -
        """
        contact_login = msg_dict['login']
        client_login = self._client_info.get_login()

        # Добавление контакта
        response_msg = None
        try:
            if self._db_connection.add_contact(client_login, contact_login) is False:
                raise SQLIntegrityError('{}, {}'.format(client_login, contact_login))

        # Если контакт не найден
        except SQLErrorNotFound as e:
            response_msg = JIMManager.create_jim_object(JSONObjectType.TO_CLIENT_ERROR, 404, str(e))

        except SQLIntegrityError as e:
            response_msg = JIMManager.create_jim_object(JSONObjectType.TO_CLIENT_ERROR, 403, str(e))

        # В случае успешного добавления контакта
        else:
            # Добавление сообщения в Log об успешном добавлении нового контакта пользователем
            self._main_window.add_data_in_tab(
                'Log', '[{}] Client {} ({}) has added client {} to his contacts.'.
                format(get_current_time(), client_login, self._client_info.get_ip(), contact_login))

            response_msg = JIMManager.create_jim_object(
                JSONObjectType.TO_CLIENT_INFO, 200, 'Contact \'{}\' has been successfully added!'.format(contact_login))

        # В любом случае необходимо ответить клиенту каким-либо сообщением
        finally:
            self._sender.add_msg_to_queue(client_login, response_msg.to_dict())

    def _client_to_server_del_contact(self, msg_dict):
        """
        Осуществляет удаление контакта у пользователя из списка контактов.
        @param msg_dict: JSON-объект (сообщение). Структура:
        {'action': self._action,
         'time': self._time,
         'login': self._login}
        @return: -
        """
        contact_login = msg_dict['login']
        client_login = self._client_info.get_login()

        # Добавление контакта
        response_msg = None
        try:
            if self._db_connection.del_contact(client_login, contact_login) is False:
                raise SQLIntegrityError('{}, {}'.format(client_login, contact_login))

        # Если контакт не найден
        except SQLErrorNotFound as e:
            response_msg = JIMManager.create_jim_object(JSONObjectType.TO_CLIENT_ERROR, 404, str(e))

        except SQLIntegrityError as e:
            response_msg = JIMManager.create_jim_object(JSONObjectType.TO_CLIENT_ERROR, 403, str(e))

        # В случае успешного удаления контакта
        else:
            # Добавление сообщения в Log об успешном удалении контакта пользователем
            self._main_window.add_data_in_tab(
                'Log', '[{}] Client {} ({}) has deleted client {} from his contacts.'.
                format(get_current_time(), client_login, self._client_info.get_ip(), contact_login))

            response_msg = JIMManager.create_jim_object(
                JSONObjectType.TO_CLIENT_INFO, 200, 'Contact \'{}\' has been successfully removed!'.format(contact_login))

        # В любом случае необходимо ответить клиенту каким-либо сообщением
        finally:
            self._sender.add_msg_to_queue(client_login, response_msg.to_dict())

    def _client_to_server_get_msgs(self, msg_dict):
        """
        Возвращает последнии сообщения, которые сохранены в БД.
        @param msg_dict: JSON-объект (сообщение). Структура:
        {'action': self._action,
         'time': self._time,
         'chat_name': self._chat_name}
        @return: -
        """
        # TODO:
        pass
