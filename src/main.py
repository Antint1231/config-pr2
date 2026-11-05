"""Инструмент визуализации графа зависимостей пакетов Alpine Linux."""
import sys
from dataclasses import asdict

from config import load_config
from errors import AppError

DEFAULT_CONFIG = "config.yaml"
ERROR_EXIT_CODE = 1


def print_params(config):
    """Выводит параметры в формате ключ-значение."""
    for key, value in asdict(config).items():
        print(f"{key}: {value}")


def main(argv):
    """Точка входа: первым аргументом передается путь к YAML-файлу."""
    path = argv[1] if len(argv) > 1 else DEFAULT_CONFIG
    try:
        config = load_config(path)
    except AppError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return ERROR_EXIT_CODE
    print_params(config)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
