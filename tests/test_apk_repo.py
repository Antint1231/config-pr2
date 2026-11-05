"""Тесты разбора репозитория apk."""
import gzip
import io
import tarfile
import unittest

from apk_repo import index_url, parse_index, strip_version, unpack_index
from errors import RepoError

INDEX = """C:Q1abc
P:musl
V:1.2.5-r0
p:so:libc.musl-x86_64.so.1=1

C:Q1def
P:openssl
V:3.3.0-r0
D:so:libc.musl-x86_64.so.1 musl>=1.2 !libressl
p:cmd:openssl=3.3.0-r0 so:libssl.so.3=3

C:Q1ghi
P:curl
V:8.0-r0
D:so:libssl.so.3 openssl>3 curl
"""


def make_archive(text):
    """Собирает в памяти архив APKINDEX.tar.gz."""
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w") as archive:
        data = text.encode("utf-8")
        info = tarfile.TarInfo("APKINDEX")
        info.size = len(data)
        archive.addfile(info, io.BytesIO(data))
    return gzip.compress(raw.getvalue())


class ApkRepoTest(unittest.TestCase):
    """Проверка разбора APKINDEX."""

    def setUp(self):
        self.repo = parse_index(INDEX)

    def test_has_package(self):
        self.assertTrue(self.repo.has_package("curl"))
        self.assertFalse(self.repo.has_package("nginx"))

    def test_version_is_removed(self):
        self.assertEqual(strip_version("musl>=1.2"), "musl")
        self.assertEqual(strip_version("a~1.0"), "a")
        self.assertEqual(strip_version("b=2"), "b")

    def test_provides_are_resolved(self):
        self.assertEqual(self.repo.dependencies("openssl"), ["musl"])

    def test_conflicts_and_self_are_skipped(self):
        self.assertEqual(self.repo.dependencies("curl"), ["openssl"])

    def test_package_without_dependencies(self):
        self.assertEqual(self.repo.dependencies("musl"), [])

    def test_unknown_dependency_stays_as_is(self):
        repo = parse_index("P:a\nD:ghost\n")
        self.assertEqual(repo.dependencies("a"), ["ghost"])

    def test_unpack_index(self):
        self.assertEqual(unpack_index(make_archive(INDEX)), INDEX)

    def test_bad_archive(self):
        with self.assertRaises(RepoError):
            unpack_index(b"this is not an archive")

    def test_index_url(self):
        base = "https://example.org/alpine/main/x86_64"
        full = base + "/APKINDEX.tar.gz"
        self.assertEqual(index_url(base), full)
        self.assertEqual(index_url(base + "/"), full)
        self.assertEqual(index_url(full), full)


if __name__ == "__main__":
    unittest.main()
