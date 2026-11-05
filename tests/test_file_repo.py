"""Тесты тестового репозитория."""
import unittest

from errors import RepoError
from file_repo import parse_graph


class FileRepoTest(unittest.TestCase):
    """Проверка разбора файла с описанием графа."""

    def test_normal(self):
        repo = parse_graph("A: B C\nB:\nC: B\n")
        self.assertEqual(repo.dependencies("A"), ["B", "C"])
        self.assertEqual(repo.dependencies("B"), [])
        self.assertTrue(repo.has_package("C"))

    def test_comments_and_empty_lines(self):
        repo = parse_graph("# комментарий\n\nA:\n")
        self.assertTrue(repo.has_package("A"))

    def test_duplicate_dependencies(self):
        repo = parse_graph("A: B B\nB:\n")
        self.assertEqual(repo.dependencies("A"), ["B"])

    def test_no_separator(self):
        with self.assertRaises(RepoError):
            parse_graph("A B\n")

    def test_bad_name(self):
        for text in ("a:\n", "A1:\n", "A: b\n"):
            with self.subTest(text=text):
                with self.assertRaises(RepoError):
                    parse_graph(text)

    def test_duplicate_package(self):
        with self.assertRaises(RepoError):
            parse_graph("A:\nA:\n")

    def test_undefined_dependency(self):
        with self.assertRaises(RepoError):
            parse_graph("A: B\n")


if __name__ == "__main__":
    unittest.main()
