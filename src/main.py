"""Инструмент визуализации графа зависимостей пакетов Alpine Linux."""
import sys

from apk_repo import load_apk_repo
from config import load_config
from errors import AppError
from file_repo import load_file_repo
from graph import build_graph, load_order
from visual import to_ascii_tree, to_mermaid

DEFAULT_CONFIG = "config.yaml"
ERROR_EXIT_CODE = 1


def make_repo(config):
    """Создает тестовый или настоящий репозиторий по настройкам."""
    if config.test_mode:
        return load_file_repo(config.repository)
    return load_apk_repo(config.repository)


def print_load_order(graph, package):
    """Выводит пакеты в порядке загрузки: сначала зависимости."""
    print(f"Порядок загрузки для пакета {package}:")
    for number, name in enumerate(load_order(graph, package), start=1):
        print(f"  {number}. {name}")


def show_result(config, graph):
    """Выводит результат в тех видах, которые включены в настройках."""
    print(to_mermaid(graph))
    if config.ascii_tree:
        print()
        print(to_ascii_tree(graph, config.package))
    if config.load_order:
        print()
        print_load_order(graph, config.package)


def run(path):
    """Загружает конфигурацию, строит граф и выводит его."""
    config = load_config(path)
    repo = make_repo(config)
    graph = build_graph(
        repo, config.package, config.max_depth, config.filter_substring
    )
    show_result(config, graph)


def main(argv):
    """Точка входа: первым аргументом передается путь к YAML-файлу."""
    path = argv[1] if len(argv) > 1 else DEFAULT_CONFIG
    try:
        run(path)
    except AppError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return ERROR_EXIT_CODE
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
