"""Тесты тестового репозитория."""
import unittest

from errors import RepoError
from file_repo import parse_graph


class FileRepoTest(unittest.TestCase):
    """Проверка разбора файла с описанием графа."""

    def test_normal(self):
        repo = parse_graph("A: B C\nB:\nC: B\n")
        self.assert_equal(repo.dependencies("A"), ["B", "C"])
        self.assert_equal(repo.dependencies("B"), [])
        self.assert_true(repo.has_package("C"))

    def test_comments_and_empty_lines(self):
        repo = parse_graph("# комментарий\n\nA:\n")
        self.assert_true(repo.has_package("A"))

    def test_duplicate_dependencies(self):
        repo = parse_graph("A: B B\nB:\n")
        self.assert_equal(repo.dependencies("A"), ["B"])

    def test_no_separator(self):
        with self.assert_raises(RepoError):
            parse_graph("A B\n")

    def test_bad_name(self):
        for text in ("a:\n", "A1:\n", "A: b\n"):
            with self.sub_test(text=text):
                with self.assert_raises(RepoError):
                    parse_graph(text)

    def test_duplicate_package(self):
        with self.assert_raises(RepoError):
            parse_graph("A:\nA:\n")

    def test_undefined_dependency(self):
        with self.assert_raises(RepoError):
            parse_graph("A: B\n")


if __name__ == "__main__":
    unittest.main()
