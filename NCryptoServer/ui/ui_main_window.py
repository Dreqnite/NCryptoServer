# -*- coding: utf-8 -*-
"""
Главное окно серверной программы чата.
"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class UiMainWindow(QMainWindow):
    """
    GUI-класс главного окна. Определяет все графические элементы и бизнес-логику.
    """
    def __init__(self, parent=None):
        """
        Конструктор. Инициализирует все графические элементы и привязывает к ним логику.
        @param parent: ссылка на родительский класс.
        """
        super(UiMainWindow, self).__init__(parent)

        self.setObjectName('SuperChatServer')

        # Настройки политики размеров по умолчанию
        self.size_policy = QSizePolicy(QSizePolicy.Preferred,
                                       QSizePolicy.Preferred)
        self.size_policy.setHorizontalStretch(0)
        self.size_policy.setVerticalStretch(0)
        self.size_policy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())

        # Делаем невозможным изменение размеров окна
        self.resize(1000, 904)
        self.setMinimumSize(QSize(1000, 904))
        self.setMaximumSize(QSize(1000, 904))

        # Главная панель клиентской области
        self.background_panel = QWidget(self)
        self.background_panel.setObjectName('background_panel')

        # Установка главной панели на окно
        self.setCentralWidget(self.background_panel)

        # Панель меню
        self.menu_bar = QMenuBar(self)
        self.menu_bar.setGeometry(QRect(0, 0, 1000, 21))
        self.menu_bar.setObjectName('menu_bar')
        self.setMenuBar(self.menu_bar)

        # StatusBar
        self.status_bar = QStatusBar(self)
        self.status_bar.setObjectName('status_bar')
        self.setStatusBar(self.status_bar)

        # Меню "File"
        self.menu_file = QMenu(self.menu_bar)
        self.menu_file.setObjectName('menu_file')

        # Пункт меню: "File" -> "Something!"
        # TODO:
        self.something_item = QAction('Something!', self)
        self.something_item.setObjectName('something_item')

        # Пункт меню: "File" -> "About"
        self.about_item = QAction('About', self)
        self.about_item.setObjectName('about_item')

        # Пункт меню: "File" -> "Exit"
        self.exit_item = QAction('Exit', self)
        self.exit_item.setObjectName('exit_item')

        # Добавление пунктов в меню "File"
        self.menu_bar.addMenu(self.menu_file)
        self.menu_file.addAction(self.something_item)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.exit_item)

        # Виджет с двумя вкладками
        self.tab_widget = QTabWidget(self.background_panel)
        self.tab_widget.setObjectName('tab_widget')
        self.tab_widget.setGeometry(QRect(8, 8, 984, 816))

        clients_tab = UiTab('Clients', QRect(8, 8, 960, 776), self.tab_widget)
        log_tab = UiTab('Log', QRect(8, 8, 960, 776), self.tab_widget)

        self.tab_widget.addTab(clients_tab, 'Clients')
        self.tab_widget.addTab(log_tab, 'Log')

        self._center_window()
        self._create_signals()
        self._retranslate_ui()

    def _create_signals(self):
        """
        Привязывает логику к графическим элементом парами "сигнал-слот".
        @return: -
        """
        self.exit_item.triggered.connect(self.close)

    def _retranslate_ui(self):
        """
        Устанавливает текст на основные графические элементы окна.
        @return: -
        """
        _translate = QCoreApplication.translate
        self.setWindowTitle(_translate('SuperChatServer', 'MainWindow'))
        self.menu_file.setTitle(_translate('SuperChatServer', 'File'))
        self.about_item.setText(_translate('SuperChatServer', 'About'))
        self.exit_item.setText(_translate('SuperChatServer', 'Exit'))

    def find_tab(self, tab_name):
        """
        Проверяет существование вкладки с данным именем.
        @param tab_name: название чата (чат-комнаты/собеседника).
        @return: индекс вкладки.
        """
        # Обрабатываем случай с единственным tab'ом отдельно, так как range() не работает
        tabs_amount = self.tab_widget.count()
        if tabs_amount == 1:
            if self.tab_widget.widget(0).name == tab_name:
                return 0
            return None

        for i in range(0, tabs_amount):
            if self.tab_widget.widget(i).name == tab_name:
                return i
        return None

    def find_row_by_data(self, tab_index, data):
        return self.tab_widget.widget(tab_index).find_row(data)

    def add_tab_data(self, tab_index, data):
        """
        Добавляет новые данные в QListWidget указанной вкладки QTabWidget.
        @param tab_index: индекс вкладки.
        @param data: новые данные.
        @return: -
        """
        self.tab_widget.widget(tab_index).add_data(data)

    def remove_tab_data(self, tab_index, data):
        """
        Удаляет строку из QListWidget на нужной вкладке.
        @param tab_index: индекс вкладки.
        @param data: данные строки для поиска.
        @return: -
        """
        tab = self.tab_widget.widget(tab_index)
        row = tab.find_row(data)
        tab.remove_data(row)

    def _center_window(self):
        """
        Отцентровывает окно на экране монитора. В расчёт берётся разрешение
        монитора пользователя.
        @return: -
        """
        resolution = QDesktopWidget().screenGeometry()
        x = (resolution.width() / 2) - (self.frameSize().width() / 2)
        y = (resolution.height() / 2) - (self.frameSize().height() / 2)
        self.move(x, y)


class UiTab(QWidget):
    """
    Класс, предназначающийся для отдельных вкладок виджета QTabWidget.
    """
    def __init__(self, name, size, parent=None):
        """
        Конструктор.
        @param name: название элемента QListWidget.
        @param size: размер элемента QListWidget.
        @param parent: ссылка на родительский класс.
        """
        super().__init__(parent)
        self.name = name
        self._content_lb = QListWidget(self)
        self._content_lb.setObjectName(name)
        self._content_lb.setGeometry(size)

    def add_data(self, data):
        """
        Добавляет новые данные в QListWidget.
        @param data: новые данные.
        @return: -
        """
        self._content_lb.addItem(data)

    def find_row(self, data):
        """
        Осуществляет поиск строки с заданными данными (тексту).
        @param data: данные (текст).
        @return: -
        """
        items_amount = self._content_lb.count()
        if items_amount == 0:
            return None

        for i in range(0, items_amount):
            if self._content_lb.item(i).text() == data:
                return i
        return None

    def remove_data(self, row):
        """
        Удаляет нужную строчку из QListWidget.
        @param row: индекс строки, которая должна быть удалена.
        @return: -
        """
        self._content_lb.takeItem(row)