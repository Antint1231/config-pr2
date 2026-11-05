"""Чтение и проверка конфигурационного файла формата YAML."""
import os
from dataclasses import dataclass

import yaml

from errors import ConfigError

DEFAULT_MAX_DEPTH = 3
URL_PREFIXES = ("http://", "https://")


@dataclass
class Config:
    """Параметры, которые задает пользователь."""

    package: str
    repository: str
    test_mode: bool = False
    ascii_tree: bool = False
    max_depth: int = DEFAULT_MAX_DEPTH
    filter_substring: str = ""
    load_order: bool = False


def read_yaml(path):
    """Читает YAML-файл и возвращает словарь с параметрами."""
    try:
        with open(path, encoding="utf-8") as file:
            data = yaml.safe_load(file)
    except OSError as error:
        raise ConfigError(f"не удалось открыть файл {path}: {error}")
    except yaml.YAMLError as error:
        raise ConfigError(f"некорректный YAML в файле {path}: {error}")
    if not isinstance(data, dict):
        raise ConfigError("конфигурация должна быть набором ключ: значение")
    return data


def get_str(data, key, required=False, default=""):
    """Возвращает строковый параметр."""
    if key not in data:
        if required:
            raise ConfigError(f"не задан обязательный параметр '{key}'")
        return default
    value = data[key]
    if not isinstance(value, str):
        raise ConfigError(f"параметр '{key}' должен быть строкой")
    if required and not value.strip():
        raise ConfigError(f"параметр '{key}' не должен быть пустым")
    return value


def get_bool(data, key, default=False):
    """Возвращает логический параметр."""
    value = data.get(key, default)
    if not isinstance(value, bool):
        raise ConfigError(f"параметр '{key}' должен быть true или false")
    return value


def get_depth(data):
    """Возвращает максимальную глубину анализа."""
    value = data.get("max_depth", DEFAULT_MAX_DEPTH)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConfigError("параметр 'max_depth' должен быть целым числом")
    if value < 0:
        raise ConfigError("параметр 'max_depth' не может быть отрицательным")
    return value


def check_repository(repository, test_mode):
    """Проверяет, что репозиторий указан правильно для выбранного режима."""
    if test_mode:
        if not os.path.isfile(repository):
            raise ConfigError(
                f"файл тестового репозитория не найден: {repository}"
            )
    elif not repository.startswith(URL_PREFIXES):
        raise ConfigError(
            "параметр 'repository' должен быть URL (http:// или https://)"
        )


def check_unknown_keys(data, allowed):
    """Ищет в конфигурации параметры, которых не существует."""
    for key in data:
        if key not in allowed:
            raise ConfigError(f"неизвестный параметр '{key}'")


def parse_config(data):
    """Создает объект Config из словаря с проверкой всех значений."""
    check_unknown_keys(data, Config.__dataclass_fields__)
    config = Config(
        package=get_str(data, "package", required=True),
        repository=get_str(data, "repository", required=True),
        test_mode=get_bool(data, "test_mode"),
        ascii_tree=get_bool(data, "ascii_tree"),
        max_depth=get_depth(data),
        filter_substring=get_str(data, "filter_substring"),
        load_order=get_bool(data, "load_order"),
    )
    check_repository(config.repository, config.test_mode)
    return config


def load_config(path):
    """Загружает конфигурацию из файла."""
    return parse_config(read_yaml(path))
