"""
Модуль для общего класса, который агрегирует функции передатчика, прёмника и обработчика.
"""
import time
from threading import Thread

from NCryptoTools.tools.utilities import get_current_time
from NCryptoTools.jim.jim_core import type_of, JIMMessage, to_bytes, to_dict, is_valid_msg
from NCryptoTools.jim.jim_constants import JIMMsgType, HTTPCode

from NCryptoServer.server_instance_holder import *
from NCryptoServer.net.server_sender import Sender
from NCryptoServer.net.server_receiver import Receiver
from NCryptoServer.database.server_storage import SQLErrorNotFound, SQLIntegrityError


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
        Runs ClientHandler thread.
        @return: None.
        """
        self._sender.start()
        self._receiver.start()
        while self._client_info.is_connected():
            msg_bytes = self._receiver.get_msg_from_queue()
            if msg_bytes is not None:
                self._handle_message(to_dict(msg_bytes))
            time.sleep(self._wait_time)

    def get_socket(self):
        """
        Возвращает сокет данного клиента.
        @return: сокет клиента.
        """
        return self._socket

    def _handle_message(self, msg_dict):
        """
        Defines message type and handles it according to the type.
        @param msg_dict: JSON message (dictionary).
        @return: None.
        """
        jim_msg_type = type_of(msg_dict)
        if jim_msg_type == JIMMsgType.UNDEFINED_TYPE or is_valid_msg(jim_msg_type, msg_dict) is False:
            return

        if jim_msg_type == JIMMsgType.CTS_AUTHENTICATE:
            self._handle_auth_msg(msg_dict)

        elif jim_msg_type == JIMMsgType.CTS_QUIT:
            self._handle_quit_msg(msg_dict)

        elif jim_msg_type == JIMMsgType.CTS_PRESENCE:
            pass

        elif jim_msg_type == JIMMsgType.CTS_PERSONAL_MSG:
            self._handle_personal_msg(msg_dict)

        elif jim_msg_type == JIMMsgType.CTS_CHAT_MSG:
            self._handle_chat_msg(msg_dict)

        elif jim_msg_type == JIMMsgType.CTS_JOIN_CHAT:
            self._handle_join_chat_msg(msg_dict)

        elif jim_msg_type == JIMMsgType.CTS_LEAVE_CHAT:
            self._handle_leave_chat_msg(msg_dict)

        elif jim_msg_type == JIMMsgType.CTS_GET_CONTACTS:
            self._handle_get_contacts_msg()

        elif jim_msg_type == JIMMsgType.CTS_ADD_CONTACT:
            self._handle_add_contact_msg(msg_dict)

        elif jim_msg_type == JIMMsgType.CTS_DEL_CONTACT:
            self._handle_del_contact_msg(msg_dict)

    def _send_broadcast(self, recipients_logins, msg_dict):
        """
        Sends message to the list of clients.
        @param recipients_logins: list of clients logins.
        @param msg_dict: JSON message (dictionary).
        @return: None.
        """
        for login in recipients_logins:
            self._sender.add_msg_to_queue(login, to_bytes(msg_dict))

    ###########################################################################
    # A group of methods to handle each of defined types of messages
    ###########################################################################
    def _handle_auth_msg(self, msg_dict):
        """
        Authenticates client by checking hist account in the database.
        @param msg_dict: JSON message (dictionary).
        @return: None.
        """
        client_login = msg_dict['user']['login']
        client_password = msg_dict['user']['password']

        authentication_success = self._db_connection.authenticate_client(client_login, client_password)
        if authentication_success is True:
            response_msg = JIMMessage(JIMMsgType.STC_ALERT,
                                      response=HTTPCode.OK,
                                      alert='Authentication is successful!')

            self._main_window.add_data_in_tab('Log', '[{}] Client ({}) has logged in as {}.'.
                                              format(get_current_time(), self._client_info.get_ip(),
                                                     client_login))

            self._main_window.add_data_in_tab('Clients', '{} ({})'.format(client_login,
                                                                          self._client_info.get_ip()))
            self._client_info.set_login(client_login)
        else:
            # if user fails authentication, a reserved login is being taken (Anonymous####)
            client_login = self._client_info.get_login()

            response_msg = JIMMessage(JIMMsgType.STC_ERROR,
                                      response=HTTPCode.UNAUTHORIZED,
                                      error='Authentication has failed!')

            self._main_window.add_data_in_tab('Log', '[{}] Client {} has failed authentication.'.
                                              format(get_current_time(), self._client_info.get_ip()))

        self._sender.add_msg_to_queue(client_login, response_msg.serialize())

    def _handle_quit_msg(self, msg_dict):
        """
        Handles user quit message, when he safely closes the connection.
        @param msg_dict: JSON message (dictionary).
        @return: None.
        """
        self._client_info.set_quit_safety(True)

        # Если пользователь не автризовался в чате, то информация, что он покинул чат,
        # остаётся только на сервере - остальным пользователям ничего не отправляем
        client_login = self._client_info.get_login()
        if client_login.startswith('Anonymous') is False:
            client_contacts = self._db_connection.get_overall_client_contacts(client_login)
            if client_contacts:
                self._send_broadcast(client_contacts, msg_dict)

            self._main_window.remove_data_from_tab('Clients', '{} ({})'.format(client_login,
                                                                               self._client_info.get_ip()))
        self._client_info.set_connection_state(False)

        self._main_window.add_data_in_tab('Log', '[{}] Client {} ({}) has closed the connection.'.
                                          format(get_current_time(), client_login,
                                                 self._client_info.get_ip()))
        # Deletes all client information which is being stored by the application
        server_holder.get_instance('ClientManager').delete_client('login', client_login)

    def _handle_personal_msg(self, msg_dict):
        """
        Handles personal message from one client to another one.
        @param msg_dict: JSON message (dictionary).
        @return: None.
        """
        recipient_login = msg_dict['to']

        error_msg = None
        if len(msg_dict['message']) == 0:
            error_msg = JIMMessage(JIMMsgType.STC_ERROR,
                                   reponse=HTTPCode.BAD_REQUEST,
                                   error='Message is empty!')

        # Recipient should be in the database
        elif self._db_connection.client_exists(recipient_login) is False:
            error_msg = JIMMessage(JIMMsgType.STC_ERROR,
                                   response=HTTPCode.NOT_FOUND,
                                   error='Client \'{}\' have not been found in the database!'.
                                   format(recipient_login))

        # Recipient should be online
        elif self._main_window.data_in_tab_exists(
                'Clients', '{} ({})'.format(recipient_login, self._client_info.get_ip())) is False:
            error_msg = JIMMessage(JIMMsgType.STC_ERROR,
                                   response=HTTPCode.NOT_FOUND,
                                   error='Client \'{}\' is not Online!'.format(recipient_login))

        if error_msg is None:
            # Message for recipient
            self._sender.add_msg_to_queue(recipient_login, to_bytes(msg_dict))

            # A reply for sender that everything is OK
            alert_msg = JIMMessage(JIMMsgType.STC_ALERT,
                                   response=HTTPCode.OK,
                                   alert='Message to \'{}\' has been delivered!'.format(recipient_login))
            self._sender.add_msg_to_queue(msg_dict['from'], alert_msg.serialize())
        else:
            self._sender.add_msg_to_queue(msg_dict['from'], error_msg.serialize())

    def _handle_chat_msg(self, msg_dict):
        """
        Handles client message to the specific chatroom.
        @param msg_dict: JSON message (dictionary).
        @return: None.
        """
        chatroom_name = msg_dict['to']

        error_msg = None
        if len(msg_dict['message']) == 0:
            error_msg = JIMMessage(JIMMsgType.STC_ERROR,
                                   reponse=HTTPCode.BAD_REQUEST,
                                   error='Message is empty!')

        # Chatroom should be in the database
        elif self._db_connection.chatroom_exists(chatroom_name) is False:
            error_msg = JIMMessage(JIMMsgType.STC_ERROR,
                                   reponse=HTTPCode.NOT_FOUND,
                                   error='Chatroom \'{}\' does not exists!'.format(chatroom_name))

        # Gets a list of chatroom participants
        chatroom_participants = self._db_connection.get_chatroom_clients(chatroom_name)
        if not chatroom_participants:
            error_msg = JIMMessage(JIMMsgType.STC_ERROR,
                                   response=HTTPCode.NOT_FOUND,
                                   error='Chatroom is empty!')

        if error_msg is None:
            # Message to the chatroom (for all its participants, except current user)
            chatroom_participants.remove(msg_dict['from'])
            self._send_broadcast(chatroom_participants, msg_dict)

            # A reply for sender that everything is OK
            response_msg = JIMMessage(JIMMsgType.STC_ALERT,
                                      response=HTTPCode.OK,
                                      alert='Message to \'{}\' has been delivered!'.format(chatroom_name))
            self._sender.add_msg_to_queue(msg_dict['from'], response_msg.serialize())
        else:
            self._sender.add_msg_to_queue(msg_dict['from'], error_msg.serialize())

    def _handle_join_chat_msg(self, msg_dict):
        """
        Handles message when client joins the specific chatroom.
        @param msg_dict: JSON message (dictionary).
        @return: None.
        """
        chatroom_name = msg_dict['room']
        client_login = self._client_info.get_login()

        response_msg = None
        try:
            if self._db_connection.add_client_to_chatroom(client_login, chatroom_name) is False:
                raise SQLIntegrityError('{}, {}'.format(client_login, chatroom_name))
        except SQLErrorNotFound as e:
            response_msg = JIMMessage(JIMMsgType.STC_ERROR,
                                      response=HTTPCode.NOT_FOUND,
                                      error=str(e))
        except SQLIntegrityError as e:
            response_msg = JIMMessage(JIMMsgType.STC_ERROR,
                                      response=HTTPCode.INTERNAL_SERVER_ERROR,
                                      error=str(e))
        else:
            response_msg = JIMMessage(JIMMsgType.STC_ALERT,
                                      response=HTTPCode.OK,
                                      alert='You have joined \'{}\' chatroom!'.format(chatroom_name))

            chatroom_participants = self._db_connection.get_chatroom_clients(chatroom_name)
            if chatroom_participants:
                self._send_broadcast(chatroom_participants, msg_dict)

            self._main_window.add_data_in_tab('Log', '[{}] Client {} ({}) has joined {}.'.format(
                get_current_time(), client_login, self._client_info.get_ip(), chatroom_name))
        finally:
            self._sender.add_msg_to_queue(client_login, response_msg.serialize())

    def _handle_leave_chat_msg(self, msg_dict):
        """
        Handles message when client leaves the specific chatroom.
        @param msg_dict: JSON message (dictionary).
        @return: None.
        """
        chatroom_name = msg_dict['room']
        client_login = self._client_info.get_login()

        response_msg = None
        try:
            if self._db_connection.del_client_from_chatroom(client_login, chatroom_name) is False:
                raise SQLIntegrityError('{}, {}'.format(client_login, chatroom_name))
        except SQLErrorNotFound as e:
            response_msg = JIMMessage(JIMMsgType.STC_ERROR,
                                      response=HTTPCode.NOT_FOUND,
                                      error=str(e))
        except SQLIntegrityError as e:
            response_msg = JIMMessage(JIMMsgType.STC_ERROR,
                                      response=HTTPCode.INTERNAL_SERVER_ERROR,
                                      error=str(e))
        else:
            response_msg = JIMMessage(JIMMsgType.STC_ALERT,
                                      response=HTTPCode.OK,
                                      alert='You have left \'{}\' chatroom!'.format(chatroom_name))

            chatroom_participants = self._db_connection.get_chatroom_clients(chatroom_name)
            if chatroom_participants:
                self._send_broadcast(chatroom_participants, msg_dict)

            self._main_window.add_data_in_tab('Log', '[{}] Client {} ({}) has left {}.'.format(
                get_current_time(), client_login, self._client_info.get_ip(), chatroom_name))
        finally:
            self._sender.add_msg_to_queue(client_login, response_msg.serialize())

    def _handle_get_contacts_msg(self):
        """
        Sends information to client with amount of his contacts and list of contacts logins.
        @return: None.
        """
        client_login = self._client_info.get_login()

        self._main_window.add_data_in_tab(
            'Log', '[{}] Client {} ({}) requested list of contacts.'.
            format(get_current_time(), client_login, self._client_info.get_ip()))

        client_contacts = self._db_connection.get_client_contacts(client_login)
        client_contacts.extend(self._db_connection.get_client_chatrooms(client_login))
        if client_contacts:
            msgs_to_send = [JIMMessage(JIMMsgType.STC_QUANTITY,
                                       response=HTTPCode.ACCEPTED,
                                       quantity=len(client_contacts))]

            for login in client_contacts:
                msgs_to_send.append(JIMMessage(JIMMsgType.STC_CONTACTS_LIST,
                                               action='contacts_list',
                                               login=login))

            for msg_to_send in msgs_to_send:
                self._sender.add_msg_to_queue(client_login, msg_to_send.serialize())

                # TODO: delay (tmp solution) to avoid sticking of messages
                time.sleep(0.1)
        else:
            response_msg = JIMMessage(JIMMsgType.STC_ERROR,
                                      response=HTTPCode.NOT_FOUND,
                                      error='No contacts were found!')
            self._sender.add_msg_to_queue(client_login, response_msg.serialize())

    def _handle_add_contact_msg(self, msg_dict):
        """
        Adds new contact to the client list.
        @param msg_dict: JSON message (dictionary).
        @return: None.
        """
        contact_login = msg_dict['login']
        client_login = self._client_info.get_login()
        response_msg = None
        try:
            if self._db_connection.add_contact(client_login, contact_login) is False:
                raise SQLIntegrityError('{}, {}'.format(client_login, contact_login))
        except SQLErrorNotFound as e:
            response_msg = JIMMessage(JIMMsgType.STC_ERROR,
                                      response=HTTPCode.NOT_FOUND,
                                      error=str(e))
        except SQLIntegrityError as e:
            response_msg = JIMMessage(JIMMsgType.STC_ERROR,
                                      response=HTTPCode.INTERNAL_SERVER_ERROR,
                                      error=str(e))
        else:
            self._main_window.add_data_in_tab(
                'Log', '[{}] Client {} ({}) has added client {} to his contacts.'.
                format(get_current_time(), client_login, self._client_info.get_ip(), contact_login))

            response_msg = JIMMessage(JIMMsgType.STC_ALERT,
                                      response=HTTPCode.OK,
                                      alert='Contact \'{}\' has been successfully added!'.format(contact_login))
        finally:
            self._sender.add_msg_to_queue(client_login, response_msg.serialize())

    def _handle_del_contact_msg(self, msg_dict):
        """
        Removes specific contact from the client list.
        @param msg_dict: JSON message (dictionary).
        @return: None.
        """
        contact_login = msg_dict['login']
        client_login = self._client_info.get_login()
        response_msg = None
        try:
            if self._db_connection.del_contact(client_login, contact_login) is False:
                raise SQLIntegrityError('{}, {}'.format(client_login, contact_login))
        except SQLErrorNotFound as e:
            response_msg = JIMMessage(JIMMsgType.STC_ERROR,
                                      response=HTTPCode.NOT_FOUND,
                                      error=str(e))
        except SQLIntegrityError as e:
            response_msg = JIMMessage(JIMMsgType.STC_ERROR,
                                      response=HTTPCode.INTERNAL_SERVER_ERROR,
                                      error=str(e))
        else:
            self._main_window.add_data_in_tab(
                'Log', '[{}] Client {} ({}) has deleted client {} from his contacts.'.
                format(get_current_time(), client_login, self._client_info.get_ip(), contact_login))

            response_msg = JIMMessage(JIMMsgType.STC_ALERT,
                                      response=HTTPCode.OK,
                                      alert='Contact \'{}\' has been successfully removed!'.format(contact_login))
        finally:
            self._sender.add_msg_to_queue(client_login, response_msg.serialize())
