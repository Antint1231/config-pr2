"""Получение зависимостей из репозитория Alpine Linux (формат apk).

Список пакетов лежит в файле APKINDEX.tar.gz. Внутри архива есть
текстовый файл APKINDEX, где пакеты разделены пустой строкой, а каждая
строка пакета имеет вид «буква:значение». Нужные поля:

    P - имя пакета
    D - зависимости через пробел
    p - что пакет предоставляет (provides)
"""
import io
import re
import tarfile
import urllib.error
import urllib.request

from errors import RepoError

INDEX_FILE = "APKINDEX"
INDEX_ARCHIVE = "APKINDEX.tar.gz"
TIMEOUT_SECONDS = 30
FIELD_RE = re.compile(r"^([A-Za-z]):(.*)$")
NAME_RE = re.compile(r"^[^<>=~]+")
CONFLICT_MARK = "!"


def index_url(url):
    """Строит адрес файла APKINDEX.tar.gz по адресу репозитория."""
    url = url.rstrip("/")
    if url.endswith(INDEX_ARCHIVE):
        return url
    return url + "/" + INDEX_ARCHIVE


def unpack_index(data):
    """Достает текст файла APKINDEX из байтов архива."""
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
            text = archive.extractfile(INDEX_FILE).read()
    except (tarfile.TarError, KeyError, OSError, EOFError) as error:
        raise RepoError(f"некорректный архив {INDEX_ARCHIVE}: {error}")
    return text.decode("utf-8", errors="replace")


def download_index(url):
    """Скачивает индекс репозитория и возвращает его текст."""
    full_url = index_url(url)
    try:
        with urllib.request.urlopen(full_url, timeout=TIMEOUT_SECONDS) as f:
            data = f.read()
    except (urllib.error.URLError, ValueError, OSError) as error:
        raise RepoError(f"не удалось скачать {full_url}: {error}")
    return unpack_index(data)


def strip_version(item):
    """Отрезает от зависимости условие на версию: 'musl>=1.2' -> 'musl'."""
    match = NAME_RE.match(item)
    return match.group() if match else item


def parse_block(block):
    """Превращает блок текста одного пакета в словарь полей."""
    fields = {}
    for line in block.splitlines():
        match = FIELD_RE.match(line)
        if match:
            fields[match.group(1)] = match.group(2)
    return fields


class ApkRepo:
    """Репозиторий apk: хранит зависимости и таблицу provides."""

    def __init__(self, packages, providers):
        self.packages = packages
        self.providers = providers

    def has_package(self, name):
        """Есть ли пакет с таким именем в репозитории."""
        return name in self.packages

    def resolve(self, item):
        """Находит имя пакета, который удовлетворяет зависимости."""
        name = strip_version(item)
        if name in self.packages:
            return name
        return self.providers.get(name, name)

    def dependencies(self, name):
        """Возвращает список прямых зависимостей пакета без повторов."""
        result = []
        for item in self.packages.get(name, []):
            if item.startswith(CONFLICT_MARK):
                continue
            target = self.resolve(item)
            if target != name and target not in result:
                result.append(target)
        return result


def parse_index(text):
    """Разбирает текст APKINDEX и создает объект ApkRepo."""
    packages = {}
    providers = {}
    for block in text.split("\n\n"):
        fields = parse_block(block)
        name = fields.get("P")
        if not name or name in packages:
            continue
        packages[name] = fields.get("D", "").split()
        for item in fields.get("p", "").split():
            providers.setdefault(strip_version(item), name)
    return ApkRepo(packages, providers)


def load_apk_repo(url):
    """Скачивает и разбирает репозиторий по URL."""
    return parse_index(download_index(url))
