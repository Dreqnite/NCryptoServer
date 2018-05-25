# -*- coding: utf-8 -*-
"""
Главный файл серверной части приложения, который объединяет все функциональные
модули в один.
"""
import sys

from PyQt5.QtWidgets import QApplication

from NCryptoServer.main_window import MainWindow
from NCryptoServer.server_instance_holder import server_holder
from NCryptoServer.database.server_storage import ServerRepository
from NCryptoServer.client_manager import ClientManager


def main():
    """
    Точка входа в приложение клиента. Отвечает за инициализацию ресурсов
    приложения.
    @return: код выхода из приложения.
    """
    app = QApplication(sys.argv)

    main_window = MainWindow()
    server_holder.add_instance('ServerRepository', ServerRepository())
    server_holder.add_instance('ClientManager', ClientManager())
    server_holder.add_instance('MainWindow', main_window)

    main_window.show()

    # Запуск потоков обработки событий
    main_window.run()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
