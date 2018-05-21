# -*- coding: utf-8 -*-
"""
Module for NCryptoServer package distribution.
"""
from setuptools import setup, find_packages

setup(
    name='NCryptoServer',
    version='0.5.3',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'SQLAlchemy>=1.2.6',
        'PyQt5>=5.10.1',
        'NCryptoTools>=0.5.2'
    ],
    description='A server-side application of the NCryptoChat',
    author='Andrew Krylov',
    author_email='AndrewKrylovNegovsky@gmail.com',
    license='GNU General Public License v3.0',
    keywords=['Server', 'Database', 'PyQt5', 'Threads', 'SQLAlchemy'],
    entry_points={
        'console_scripts': ['NCryptoServer_console = NCryptoServer.launcher:main'],
        'gui_scripts': ['NCryptoServer_gui = NCryptoServer.launcher:main']
    }
)
