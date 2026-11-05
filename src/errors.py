"""Исключения приложения."""


class AppError(Exception):
    """Базовая ошибка приложения."""


class ConfigError(AppError):
    """Ошибка в конфигурационном файле."""


class RepoError(AppError):
    """Ошибка при работе с репозиторием пакетов."""
