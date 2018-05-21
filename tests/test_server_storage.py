# -*- coding: utf-8 -*-
"""
Module for testing of the test_server_storage.py
"""
import unittest
from parameterized import parameterized
from NCryptoServer.Database.server_storage import ServerRepository


class TestServerRepository(unittest.TestCase):
    def setUp(self):
        self._repo = ServerRepository()

    @parameterized.expand([
        ('john777', 'qwerty', True),
        ('rosk1ng', '54321', False),
        ('N4stya', 'rfvtgb', True)
    ])
    def test_authenticate_client(self, login, password, expected):
        """
        Tests function authenticate_client() from the server_storage.py.
        @param login: client login
        @param password: client password.
        @param expected: expected result (boolean).
        @return: -
        """
        result = self._repo.authenticate_client(login, password)
        assert expected == result

    def test_add_client(self):
        """
        Tests function add_client() from the server_storage.py.
        @return: -
        """
        result = self._repo.add_client('Alien', 'edcrfvtgb', 'Elena Topalova', None)
        assert result

    def test_add_contact(self):
        """
        Tests function add_contact() from the server_storage.py.
        @return: -
        """
        result = self._repo.add_contact('Irene', 'N4stya')
        assert result

    @parameterized.expand([
        ('man454', False),
        ('N4stya', True)
    ])
    def test_client_exists(self, login, expected):
        """
        Tests function client_exists() from the server_storage.py.
        @param login: client login.
        @param expected: expected result (boolean).
        @return: -
        """
        result = self._repo.client_exists(login)
        assert expected == result

    @parameterized.expand([
        ('#hh', False),
        ('#GeekBrains', True)
    ])
    def test_chatroom_exists(self, chatroom_name, expected):
        """
        Tests function chatroom_exists() from the server_storage.py.
        @param chatroom_name: chatroom name.
        @param expected: expected result (boolean).
        @return: -
        """
        result = self._repo.chatroom_exists(chatroom_name)
        assert expected == result

    def test_get_client_by_login(self):
        """
        Tests function get_client_by_login() from the server_storage.py.
        @return: -
        """
        result = self._repo.get_client_by_login('john777')
        assert result is not None

    def test_get_client_contacts(self):
        """
        Tests function get_client_contacts() from the server_storage.py.
        @return: -
        """
        result = self._repo.get_client_contacts('Dreqn1te')
        assert len(result) == 5

    def test_get_client_chatrooms(self):
        """
        Tests function get_client_chatrooms() from the server_storage.py.
        @return: -
        """
        result = self._repo.get_client_chatrooms('Dreqn1te')
        assert len(result) == 4

    def test_get_chatroom_clients(self):
        """
        Tests function get_chatroom_clients() from the server_storage.py.
        @return: -
        """
        result = self._repo.get_chatroom_clients('#GeekBrains')
        assert len(result) == 7

    @parameterized.expand([
        ('Dreqn1te', '#StackOverflow', True),
        ('Irene', '#Python', False)
    ])
    def test_is_client_in_chatroom(self, login, chatroom_name, expected):
        """
        Tests function is_client_in_chatroom() from the server_storage.py.
        @param login: client login.
        @param chatroom_name: chatroom name.
        @param expected: expected result.
        @return: -
        """
        result = self._repo.is_client_in_chatroom(login, chatroom_name)
        assert expected == result

    def test_del_contact(self):
        """
        Tests function del_contact() from the server_storage.py.
        @return: -
        """
        result = self._repo.del_contact('john777', 'rosk1ng')
        assert result

    def test_get_chatroom_by_name(self):
        """
        Tests function get_chatroom_by_name() from the server_storage.py.
        @return: -
        """
        result = self._repo.get_chatroom_by_name('#StackOverflow')
        assert result is not None

    def test_add_client_to_chatroom(self):
        """
        Tests function add_client_to_chatroom() from the server_storage.py.
        @return: -
        """
        result = self._repo.add_client_to_chatroom('john777', '#Python')
        assert result

    def test_del_client_from_chatroom(self):
        """
        Tests function del_client_from_chatroom() from the server_storage.py.
        @return: -
        """
        result = self._repo.add_client_to_chatroom('john777', '#Python')
        assert result

    def test_get_overall_client_contacts(self):
        """
        Tests function get_overall_client_contacts() from the server_storage.py.
        @return: -
        """
        result = self._repo.get_overall_client_contacts('Dreqn1te')
        assert list(set(result)) == result
