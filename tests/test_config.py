"""Тесты чтения конфигурации."""
import os
import tempfile
import unittest

from config import DEFAULT_MAX_DEPTH, load_config
from errors import ConfigError


class ConfigTest(unittest.TestCase):
    """Проверка load_config на правильных и неправильных файлах."""

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.repo = self.write("repo.txt", "A:\n")

    def write(self, name, text):
        """Создает файл во временной папке и возвращает путь."""
        path = os.path.join(self.dir.name, name)
        with open(path, "w", encoding="utf-8") as file:
            file.write(text)
        return path

    def load(self, text):
        """Записывает конфигурацию в файл и загружает ее."""
        return load_config(self.write("config.yaml", text))

    def test_full_config(self):
        config = self.load(
            f"package: A\nrepository: {self.repo}\ntest_mode: true\n"
            "ascii_tree: true\nmax_depth: 5\nfilter_substring: lib\n"
        )
        self.assertEqual(config.package, "A")
        self.assertTrue(config.test_mode)
        self.assertTrue(config.ascii_tree)
        self.assertEqual(config.max_depth, 5)
        self.assertEqual(config.filter_substring, "lib")

    def test_defaults(self):
        config = self.load("package: nginx\nrepository: https://a.b/c\n")
        self.assertFalse(config.test_mode)
        self.assertEqual(config.max_depth, DEFAULT_MAX_DEPTH)
        self.assertEqual(config.filter_substring, "")

    def test_missing_file(self):
        with self.assertRaises(ConfigError):
            load_config("no_such_file.yaml")

    def test_broken_yaml(self):
        with self.assertRaises(ConfigError):
            self.load("package: [A\n")

    def test_not_a_mapping(self):
        with self.assertRaises(ConfigError):
            self.load("- A\n- B\n")

    def test_missing_package(self):
        with self.assertRaises(ConfigError):
            self.load("repository: https://a.b/c\n")

    def test_empty_package(self):
        with self.assertRaises(ConfigError):
            self.load("package: ''\nrepository: https://a.b/c\n")

    def test_bad_url(self):
        with self.assertRaises(ConfigError):
            self.load("package: A\nrepository: ftp://a.b/c\n")

    def test_missing_test_repo_file(self):
        with self.assertRaises(ConfigError):
            self.load("package: A\nrepository: nope.txt\ntest_mode: true\n")

    def test_bad_bool(self):
        with self.assertRaises(ConfigError):
            self.load("package: A\nrepository: https://a.b/c\n"
                      "ascii_tree: yes please\n")

    def test_bad_depth(self):
        for value in ("abc", "-1", "1.5", "true"):
            with self.subTest(value=value):
                with self.assertRaises(ConfigError):
                    self.load("package: A\nrepository: https://a.b/c\n"
                              f"max_depth: {value}\n")

    def test_unknown_key(self):
        with self.assertRaises(ConfigError):
            self.load("package: A\nrepository: https://a.b/c\ncolor: red\n")


if __name__ == "__main__":
    unittest.main()
