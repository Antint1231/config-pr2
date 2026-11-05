"""Тестовый репозиторий: граф зависимостей из текстового файла.

Каждая строка файла описывает один пакет в виде «A: B C», где A - имя
пакета, а B и C - его зависимости. Имена состоят из больших латинских
букв. Пустые строки и строки, начинающиеся с «#», пропускаются.
"""
import re

from errors import RepoError

NAME_RE = re.compile(r"^[A-Z]+$")
COMMENT_MARK = "#"
SEPARATOR = ":"


class FileRepo:
    """Репозиторий, заданный словарем «пакет: список зависимостей»."""

    def __init__(self, packages):
        self.packages = packages

    def has_package(self, name):
        """Есть ли пакет с таким именем."""
        return name in self.packages

    def dependencies(self, name):
        """Возвращает список прямых зависимостей без повторов."""
        return list(dict.fromkeys(self.packages.get(name, [])))


def check_name(name, line_number):
    """Проверяет, что имя состоит только из больших латинских букв."""
    if not NAME_RE.match(name):
        raise RepoError(
            f"строка {line_number}: недопустимое имя пакета '{name}'"
        )


def parse_line(line, line_number):
    """Разбирает строку вида 'A: B C' и возвращает имя и зависимости."""
    if SEPARATOR not in line:
        raise RepoError(f"строка {line_number}: нет символа '{SEPARATOR}'")
    name, _, rest = line.partition(SEPARATOR)
    name = name.strip()
    dependencies = rest.split()
    for item in [name] + dependencies:
        check_name(item, line_number)
    return name, dependencies


def parse_graph(text):
    """Разбирает текст описания графа и создает FileRepo."""
    packages = {}
    for number, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line or line.startswith(COMMENT_MARK):
            continue
        name, dependencies = parse_line(line, number)
        if name in packages:
            raise RepoError(f"строка {number}: пакет '{name}' описан дважды")
        packages[name] = dependencies
    check_all_defined(packages)
    return FileRepo(packages)


def check_all_defined(packages):
    """Проверяет, что каждая зависимость тоже описана в файле."""
    for name, dependencies in packages.items():
        for item in dependencies:
            if item not in packages:
                raise RepoError(
                    f"пакет '{item}' (зависимость '{name}') не описан"
                )


def load_file_repo(path):
    """Читает файл тестового репозитория."""
    try:
        with open(path, encoding="utf-8") as file:
            text = file.read()
    except OSError as error:
        raise RepoError(f"не удалось прочитать {path}: {error}")
    return parse_graph(text)
