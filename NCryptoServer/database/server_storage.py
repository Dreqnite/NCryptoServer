# -*- coding: utf-8 -*-
"""
Module for server repository.
"""
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, scoped_session

from NCryptoServer.Database.db_model import *


class SQLErrorNotFound(Exception):
    """
    Class for exceptions when entry was not found in the database.
    """
    def __init__(self, object_name):
        """
        Constructor.
        @param object_name: object name (which caused an error).
        """
        self._object_name = object_name

    def __str__(self):
        """
        Shows exception string.
        @return: exception text.
        """
        return 'SQL-error: object(s) \'{}\' have not been found!'.format(self._object_name)


class SQLIntegrityError(Exception):
    """
    Class fo exceptions when entry already exists in the database and
    some other cases.
    """
    def __init__(self, object_name):
        """
        Constructor.
        @param object_name: object name (which caused an error).
        """
        self._object_name = object_name

    def __str__(self):
        """
        Shows exception string.
        @return: exception text.
        """
        return 'SQL integrity error: failed to commit object(s) \'{}\'!'.format(self._object_name)


class ServerRepository:
    """
    Repository class. Performs all kinds of actions related to adding, deleting
    and updating data in the database.
    """
    def __init__(self):
        """
        Constructor.
        """
        self._db_engine = create_engine('sqlite:///{}'.format(DB_PATH))
        Base.metadata.create_all(self._db_engine)

        # Sessions in the SQLAlchemy are ThreadLocal:
        # http://docs.sqlalchemy.org/en/latest/orm/contextual.html
        self._generate_session = scoped_session(sessionmaker(bind=self._db_engine))

    def authenticate_client(self, login, password):
        """
        Authenticates client by comparison of passwords storing in the database
        with passwords, passed in the args.
        @param login: client login.
        @param password: client password.
        @return: result of authentication (boolean).
        """
        session = self._generate_session()

        query_password = session.query(Client.password).filter(Client.login == login).first()
        if query_password is None:
            return False

        session.close()

        # Tuple is resurned, we take the first value
        return query_password[0] == password

    def add_client(self, login, password, name, info=None):
        """
        Adds client in the database in the table 'client'.
        @param login: client login.
        @param password: client password.
        @param name: client real name.
        @param info: additional information (optional).
        @return: result of client adding (boolean).
        """
        session = self._generate_session()

        new_item = Client(login, password, name, info)

        session.add(new_item)

        result = True
        try:
            session.commit()
        except IntegrityError:
            result = False
            session.rollback()
        finally:
            session.close()

        return result

    def add_contact(self, client_login, contact_login):
        """
        Adds contact in the database in the instance 'contacts'. Adds a pair of entries:
        - adds contact into the client's list.
        - adds client into the contact's list.
        Because the only possible way for chatting is to have mutual contacts.
        @param client_login: client login.
        @param contact_login: contact login.
        @return: result of contact adding (boolean).
        """
        query_contact = self.get_client_by_login(contact_login)
        if query_contact is None:
            raise SQLErrorNotFound(contact_login)

        query_client = self.get_client_by_login(client_login)
        if query_client is None:
            raise SQLErrorNotFound(client_login)

        session = self._generate_session()

        client_contact = ClientContacts(query_client.id, query_contact.id)
        contact_client = ClientContacts(query_contact.id, query_client.id)

        session.add(client_contact)
        session.add(contact_client)

        result = True
        try:
            session.commit()
        except IntegrityError:
            result = False
            session.rollback()
        finally:
            session.close()

        return result

    def del_contact(self, client_login, contact_login):
        """
        Deletes contacts from the database from the instance 'contacts'. Deletes a pair of entries:
        - deletes contact from the client's list.
        - deletes client from the contact's list.
        Because the only possible way for chatting is to have mutual contacts.
        @param client_login: client login.
        @param contact_login: contact login.
        @return: result of contact deleting (boolean).
        """
        query_contact = self.get_client_by_login(contact_login)
        if query_contact is None:
            raise SQLErrorNotFound(contact_login)

        query_client = self.get_client_by_login(client_login)
        if query_client is None:
            raise SQLErrorNotFound(client_login)

        session = self._generate_session()

        query_client_contact = session.query(ClientContacts).\
            filter(ClientContacts.id_client_one == query_client.id,
                   ClientContacts.id_client_two == query_contact.id).first()
        if query_client_contact is None:
            raise SQLErrorNotFound(str(query_client.id) + ', ' + str(query_contact.id))

        query_contact_client = session.query(ClientContacts).\
            filter(ClientContacts.id_client_one == query_contact.id,
                   ClientContacts.id_client_two == query_client.id).first()
        if query_contact_client is None:
            raise SQLErrorNotFound(str(query_contact.id) + ', ' + str(query_client.id))

        session.delete(query_client_contact)
        session.delete(query_contact_client)

        result = True
        try:
            session.commit()
        except IntegrityError:
            result = False
            session.rollback()
        finally:
            session.close()

        return result

    def client_exists(self, login):
        """
        Checks existence of client in the 'client' table in the database.
        @param login: client login.
        @return: result of checking of client existence (boolean).
        """
        session = self._generate_session()

        query_client = session.query(Client).filter(Client.login == login).count()

        session.close()

        return query_client > 0

    def chatroom_exists(self, chatroom_name):
        """
        Checks existence of chatroom in the 'chatroom' table in the database.
        @param chatroom_name: chatroom name.
        @return: result of checking of chatroom existence (boolean).
        """
        session = self._generate_session()

        query_chatroom = session.query(Chatroom).filter(Chatroom.name == chatroom_name).count()

        session.close()

        return query_chatroom > 0

    def get_client_by_login(self, login):
        """
        Gets client entry by login.
        @param login: client login.
        @return: client entry.
        """
        session = self._generate_session()

        query_client = session.query(Client).filter(Client.login == login).first()

        session.close()

        return query_client

    def get_client_contacts(self, login):
        """
        Gets the list of all contacts which are in the list of client contacts.
        @param login: client login.
        @return: list of contacts logins.
        """
        session = self._generate_session()

        # Takes the id of the first user from the 'client' table by the login
        query_client_id = session.query(Client.id).filter(Client.login == login).first()
        if query_client_id is None:
            raise SQLErrorNotFound(login)

        # Gets a list of user contacts ids
        query_contacts_id_list = session.query(ClientContacts.id_client_two).\
            filter(ClientContacts.id_client_one == query_client_id[0])
        if query_contacts_id_list is None:
            raise SQLErrorNotFound(query_client_id[0])

        # Gets a list of logins by contacts ids
        contacts = []
        for i in range(0, query_contacts_id_list.count()):
            query_login = session.query(Client.login).\
                filter(Client.id == query_contacts_id_list[i][0]).first()
            if query_login is None:
                raise SQLErrorNotFound(query_contacts_id_list[i][0])
            contacts.append(query_login[0])

        session.close()

        return contacts

    def get_client_chatrooms(self, login):
        """
        Gets the list of all chatrooms which are in the list of client contacts.
        @param login: client login.
        @return: list of chatrooms names.
        """
        session = self._generate_session()

        # Takes the id of the first user from the 'client' table by the login
        query_client_id = session.query(Client.id).filter(Client.login == login).first()
        if query_client_id is None:
            raise SQLErrorNotFound(login)

        # Gets a list of user chatrooms ids
        query_chatroom_id_list = session.query(ChatroomClient.id_chatroom).\
            filter(ChatroomClient.id_client == query_client_id[0])
        if query_chatroom_id_list is None:
            raise SQLErrorNotFound(query_client_id)

        # Gets a list of chatrooms names by contacts ids
        chatrooms = []
        for i in range(0, query_chatroom_id_list.count()):
            query_name = session.query(Chatroom.name).\
                filter(Chatroom.id == query_chatroom_id_list[i][0]).first()
            if query_name is None:
                raise SQLErrorNotFound(query_chatroom_id_list[i][0])
            chatrooms.append(query_name[0])

        session.close()

        return chatrooms

    def get_chatroom_clients(self, chatroom_name):
        """
        Gets the list of logins of chatroom participants.
        @param chatroom_name: chatroom name.
        @return: list of logins of chatroom participants.
        """
        session = self._generate_session()

        # Берёт Id чат комнаты
        query_chatroom_id = session.query(Chatroom.id).filter(Chatroom.name == chatroom_name).first()
        if query_chatroom_id is None:
            raise SQLErrorNotFound(chatroom_name)

        # По Id чат комнаты берёт список Id клиентов, которые там состоят
        query_client_id_list = session.query(ChatroomClient.id_client).\
            filter(ChatroomClient.id_chatroom == query_chatroom_id[0])
        if query_client_id_list is None:
            raise SQLErrorNotFound(query_chatroom_id[0])

        client_name_list = []
        for i in range(0, query_client_id_list.count()):
            query_login = session.query(Client.login).\
                filter(Client.id == query_client_id_list[i][0]).first()
            if query_login is None:
                raise SQLErrorNotFound(query_client_id_list[i][0])
            client_name_list.append(query_login[0])

        session.close()

        return client_name_list

    def is_client_in_chatroom(self, login, chatroom_name):
        """
        Checks whether the user with defined login is a chatroom participant or not.
        @param login: client login.
        @param chatroom_name: chatroom name.
        @return: result of checking (boolean).
        """
        client_chatrooms = self.get_client_chatrooms(login)
        return chatroom_name in client_chatrooms

    def get_chatroom_by_name(self, chatroom_name):
        """
        Gets chatroom entry by its name.
        @param chatroom_name: chatroom name.
        @return: -
        """
        session = self._generate_session()

        query_chatroom = session.query(Chatroom).filter(Chatroom.name == chatroom_name).first()

        session.close()

        return query_chatroom

    def add_client_to_chatroom(self, login, chatroom_name):
        """
        Adds client to the list of chatroom participants.
        @param login: client login.
        @param chatroom_name: chatroom name.
        @return: result of client adding (boolean).
        """
        session = self._generate_session()

        query_client = self.get_client_by_login(login)
        if query_client is None:
            raise SQLErrorNotFound(login)

        query_chatroom = self.get_chatroom_by_name(chatroom_name)
        if query_chatroom is None:
            raise SQLErrorNotFound(chatroom_name)

        query_client_chatroom = ChatroomClient(query_client.id, query_chatroom.id)
        if query_client_chatroom is None:
            raise SQLErrorNotFound(str(query_client.id) + ', ' + str(query_chatroom.id))

        session.add(query_client_chatroom)

        result = True
        try:
            session.commit()
        except IntegrityError:
            result = False
            session.rollback()
        finally:
            session.close()

        return result

    def del_client_from_chatroom(self, login, chatroom_name):
        """
        Deletes client from the list of chatroom participants.
        @param login: client login.
        @param chatroom_name: chatroom name.
        @return: result of client deleting (boolean).
        """
        session = self._generate_session()

        query_client = self.get_client_by_login(login)
        if query_client is None:
            raise SQLErrorNotFound(login)

        query_chatroom = self.get_chatroom_by_name(chatroom_name)
        if query_chatroom is None:
            raise SQLErrorNotFound(chatroom_name)

        query_client_chatroom = session.query(ChatroomClient).\
            filter(ChatroomClient.id_client == query_client.id,
                   ChatroomClient.id_chatroom == query_chatroom.id).first()

        if query_client_chatroom is None:
            raise SQLErrorNotFound(str(query_client.id) + ', ' + str(query_chatroom.id))

        session.delete(query_client_chatroom)

        result = True
        try:
            session.commit()
        except IntegrityError:
            result = False
            session.rollback()
        finally:
            session.close()

        return result

    def get_overall_client_contacts(self, login):
        """
        Gets overall list of contacts including:
        - list of direct contacts (persons);
        - list of all chatrooms participants where the current user is.
        Note: only unique logins.
        @param login: client login.
        @return: overall list of logins.
        """
        client_contacts = self.get_client_contacts(login)
        client_chatrooms = self.get_client_chatrooms(login)

        # Mixing two list to delete repeated values, since these two lists
        # definitely overlap each other
        for chatroom_name in client_chatrooms:
            chatroom_participants = self.get_chatroom_clients(chatroom_name)
            client_contacts.extend(chatroom_participants)

        # Deletes repeated values,
        return list(set(client_contacts))
