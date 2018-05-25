# -*- coding: utf-8 -*-
"""
Главный файл серверной части приложения, который объединяет все функциональные
модули в один.
"""
from NCryptoServer.ui.ui_main_window import UiMainWindow
from NCryptoServer.net.server_connection_acceptor import ConnectionAcceptor


class MainWindow(UiMainWindow):
    """
    Class, needed for functioning of the main window.
    """
    def __init__(self):
        """
        Constructor.
        """
        super().__init__()
        self._connection_acceptor = None

    def run(self):
        """
        Запускает ConnectionAcceptor. Приходится инициализировать в отдельном
        методе, чтобы была возможность получить экземпляр MainWindow на теку-
        щем этапе. Если бы иницализация производилась в конструкторе, то эк-
        земпляр окна ещё не был бы создан, соответственно появилась бы ошибка.
        @return:
        """
        self._connection_acceptor = ConnectionAcceptor()
        self._connection_acceptor.start()

    def data_in_tab_exists(self, tab_name, data):
        index = self.find_tab(tab_name)
        if index is None:
            return None
        else:
            return self.find_row_by_data(index, data) is not None

    def add_data_in_tab(self, tab_name, data):
        """
        Добавляет строку на вкладку.
        @param tab_name: название вкладки.
        @param data: данные для добавления.
        @return: -
        """
        index = self.find_tab(tab_name)
        if index is not None:
            self.add_tab_data(index, data)

    def remove_data_from_tab(self, tab_name, data):
        """
        Deletes row from the needed tab.
        @param tab_name: tab name.
        @param data: data to be searched and deleted.
        @return: -
        """
        index = self.find_tab(tab_name)
        if index is not None:
            self.remove_tab_data(index, data)
