"""Модуль ранер для тестов."""

from types import MethodType
from typing import Any

from django.db import connections
from django.db.backends.base.base import BaseDatabaseWrapper
from django.test.runner import DiscoverRunner


def prepare_db(self):
    """Создать схему.

    Args:
        self: ...
    """
    self.connect()
    self.connection.cursor().execute('create schema if not exists hotel;')


class PostgresSchemaRunner(DiscoverRunner):
    """Класс настройки базы данных для тестов."""

    def setup_databases(self, **kwargs: Any) -> list[tuple[BaseDatabaseWrapper, str, bool]]:
        """Настройка базы данных.

        Args:
            kwargs (Any): аргументы

        Returns:
            list[tuple[BaseDatabaseWrapper, str, bool]]: настройки базы данных
        """
        for conn_name in connections:
            connection = connections[conn_name]
            connection.prepare_database = MethodType(prepare_db, connection)
        return super().setup_databases(**kwargs)
