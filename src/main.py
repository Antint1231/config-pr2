"""Инструмент визуализации графа зависимостей пакетов Alpine Linux."""
import sys

from apk_repo import load_apk_repo
from config import load_config
from errors import AppError, RepoError

DEFAULT_CONFIG = "config.yaml"
ERROR_EXIT_CODE = 1


def print_direct_dependencies(repo, package):
    """Выводит прямые зависимости пакета."""
    if not repo.has_package(package):
        raise RepoError(f"пакет '{package}' не найден в репозитории")
    print(f"Прямые зависимости пакета {package}:")
    for name in repo.dependencies(package):
        print(f"  {name}")


def run(path):
    """Загружает конфигурацию и репозиторий, выводит зависимости."""
    config = load_config(path)
    repo = load_apk_repo(config.repository)
    print_direct_dependencies(repo, config.package)


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
