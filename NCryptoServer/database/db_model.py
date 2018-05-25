# -*- coding: utf-8 -*-
"""
Module for ORM classes.
"""
import sqlite3
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from NCryptoServer.utils.constants import *


Base = declarative_base()


def get_current_max_id(table_name):
    """
    Every class is released with automatically incremented id.
    This function gets the value of the MAX id which is currently
    being stored in the database.
    @param table_name: table name.
    @return: MAX id value.
    """
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()
    cursor.execute('SELECT max(id) FROM {}'.format(table_name))
    return cursor.fetchone()[0]


class SQLError(Exception):
    """
    Class for general SQL and ORM errors.
    """
    def __init__(self, sql_error):
        """
        Constructor.
        @param sql_error: error message.
        """
        self.sql_error = sql_error

    def __str__(self):
        """
        Shows error text.
        @return: error message.
        """
        return 'SQL-error: {}'.format(self.sql_error)


class Client(Base):
    """
    Class which reflects instance 'client'.
    """
    __tablename__ = 'client'

    # PK, client id
    id = Column(Integer, primary_key=True)

    # Client's login (unique)
    login = Column(String(32), unique=True)

    # Client's password
    password = Column(String(32))

    # Client name
    name = Column(String(32))

    # Additional information (optional)
    info = Column(String(32), nullable=True)

    # Relationship: 'client' --< 'client_history'
    client_to_client_history_rel = relationship('ClientHistory',
                                                back_populates='client_history_to_client_rel')

    # Relationship: 'client' --< 'chatroom_client'
    client_to_chatroom_client_rel = relationship('ChatroomClient',
                                                 back_populates='chatroom_client_to_client_rel')

    # Counter of id, which automatically increments it when trying to add a new entry
    _autoincrement = 0 if get_current_max_id(__tablename__) is None else get_current_max_id(__tablename__)

    def __init__(self, login, password, name, info=None):
        """
        Constructor.
        @param login: user login (unique).
        @param password: user password.
        @param name: client name.
        @param info: additional information (optional).
        """
        Client._autoincrement += 1
        self.id = Client._autoincrement
        self.login = login
        self.password = password
        self.name = name
        self.info = info

    def __repr__(self):
        """
        Shows the decorated name of a client.
        @return: string with client's login.
        """
        return '<Client \'{}\'>'.format(self.login)

    def __eq__(self, other):
        """
        Compares clients logins.
        @param other: other client's instance.
        @return: boolean result of comparison.
        """
        return self.login == other.login


class ClientContacts(Base):
    """
    Class which reflects instance 'client_contacts'.
    """
    __tablename__ = 'client_contacts'

    # PK, id
    id = Column(Integer, primary_key=True)

    # FK, Client's id
    id_client_one = Column(Integer, ForeignKey('client.id'))

    # FK, Contact's id
    id_client_two = Column(Integer, ForeignKey('client.id'))

    # Relationships: 'client' --< 'contacts'
    client_contacts_to_client_rel_1 = relationship('Client',
                                                   foreign_keys='ClientContacts.id_client_one')
    client_contacts_to_client_rel_2 = relationship('Client',
                                                   foreign_keys='ClientContacts.id_client_two')

    # Counter of id, which automatically increments it when trying to add a new entry
    _autoincrement = 0 if get_current_max_id(__tablename__) is None else get_current_max_id(__tablename__)

    def __init__(self, client_id, contact_id):
        """
        Constructor.
        @param client_id: client's id.
        @param contact_id: contacts's id.
        """
        ClientContacts._autoincrement += 1
        self.id = ClientContacts._autoincrement
        self.id_client_one = client_id
        self.id_client_two = contact_id


class ClientHistory(Base):
    """
    Class which reflects instance 'client_history'.
    """
    __tablename__ = 'client_history'

    # PK, id
    id = Column(Integer, primary_key=True)

    # Connection time
    connection_time = Column(DateTime)

    # Ipv4 address
    ip = Column(String(16))

    # FK, Client id
    id_client = Column(Integer, ForeignKey('client.id'))

    # Relationship: 'client' --< 'client_history'
    client_history_to_client_rel = relationship('Client',
                                                back_populates='client_to_client_history_rel')

    # Counter of id, which automatically increments it when trying to add a new entry
    _autoincrement = 0 if get_current_max_id(__tablename__) is None else get_current_max_id(__tablename__)

    def __init__(self, connection_time, ip_address, client_id):
        """
        Constructor.
        @param connection_time: connection time
        @param ip_address: IPv4 address.
        @param client_id: client's id.
        """
        ClientHistory._autoincrement += 1
        self.id = ClientHistory._autoincrement
        self.connection_time = connection_time
        self.ip = ip_address
        self.id_client = client_id


class ChatroomClient(Base):
    """
    Class which reflects associative instance 'chatroom_client'.
    Relationship: many-to-many.
    """
    __tablename__ = 'chatroom_client'

    # PK, id
    id = Column(Integer, primary_key=True)

    # FK, Client id
    id_client = Column(Integer, ForeignKey('client.id'))

    # FK, Chatroom id
    id_chatroom = Column(Integer, ForeignKey('chatroom.id'))

    # Relationship: 'client' --< 'chatroom_client'
    chatroom_client_to_client_rel = relationship('Client',
                                                 back_populates='client_to_chatroom_client_rel')

    # Relationship: 'chatroom' --< 'chatroom_client'
    chatroom_client_to_chatroom_rel = relationship('Chatroom',
                                                   back_populates='chatroom_to_chatroom_client_rel')

    # Counter of id, which automatically increments it when trying to add a new entry
    _autoincrement = 0 if get_current_max_id(__tablename__) is None else get_current_max_id(__tablename__)

    def __init__(self, client_id, chatroom_id):
        """
        Constructor.
        @param client_id: client's id.
        @param chatroom_id: chatroom's id.
        """
        ChatroomClient._autoincrement += 1
        self.id = ChatroomClient._autoincrement
        self.id_client = client_id
        self.id_chatroom = chatroom_id


class Chatroom(Base):
    """
    Class which reflects instance 'chatroom'.
    """
    __tablename__ = 'chatroom'

    # PK, id
    id = Column(Integer, primary_key=True)

    # Chatroom name
    name = Column(String(32))

    # Relationship: 'chatroom' --< 'chatroom_client'
    chatroom_to_chatroom_client_rel = relationship('ChatroomClient',
                                                   back_populates='chatroom_client_to_chatroom_rel')

    # Relationship: 'chatroom' --< 'message'
    chatroom_to_message_rel = relationship('Message',
                                           back_populates='message_to_chatroom_rel')

    # Counter of id, which automatically increments it when trying to add a new entry
    _autoincrement = 0 if get_current_max_id(__tablename__) is None else get_current_max_id(__tablename__)

    def __init__(self, name):
        """
        Constructor.
        @param name: chatroom name.
        """
        Chatroom._autoincrement += 1
        self.id = Chatroom._autoincrement
        self.name = name


class Message(Base):
    """
    Class which reflects instance 'message'.
    """
    __tablename__ = 'message'

    # PK, id
    id = Column(Integer, primary_key=True)

    # FK, client's login (sender)
    from_client = Column(String(32), ForeignKey('client.login'))

    # FK, client's login (receiver)
    to_client = Column(String(32), ForeignKey('client.login'), nullable=True)

    # FK, chatroom's name (receiver)
    to_chatroom = Column(String(32), ForeignKey('chatroom.name'), nullable=True)

    # Message text
    message = Column(String(128))

    # Relationship: 'client' --< 'message'
    message_to_client_rel_1 = relationship('Client',
                                           foreign_keys='Message.from_client')
    # Relationship: 'client' --< 'message'
    message_to_client_rel_2 = relationship('Client',
                                           foreign_keys='Message.to_client')
    # Relationship: 'client' --< 'chatroom'
    message_to_chatroom_rel = relationship('Chatroom',
                                           back_populates='chatroom_to_message_rel')

    # Counter of id, which automatically increments it when trying to add a new entry
    _autoincrement = 0 if get_current_max_id(__tablename__) is None else get_current_max_id(__tablename__)

    def __init__(self, from_client, message, to_client=None, to_chatroom=None):
        """
        Constructor. Only one of attributes (to_client, to_chatroom) should have a value
        (not NULL), since there can be only one recipient.
        @param from_client: client's login (sender).
        @param message: message text.
        @param to_client: client's login (receiver).
        @param to_chatroom: chatroom's name (receiver).
        """
        # Checks needed constraint
        if ((to_client is None) ^ (to_chatroom is None)) is False:
            raise SQLError('SQL constraint error: multiple recipients!')

        Message._autoincrement += 1
        self.id = Message._autoincrement
        self.from_client = from_client
        self.to_client = to_client
        self.to_chatroom = to_chatroom
        self.message = message
