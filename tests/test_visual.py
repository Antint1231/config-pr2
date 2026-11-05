"""Тесты текстового представления графа."""
import unittest

from file_repo import parse_graph
from graph import build_graph
from visual import to_ascii_tree, to_mermaid

BASIC = "A: B C\nB: D\nC: D E\nD: F\nE:\nF:\n"
CYCLE = "A: B\nB: C\nC: A\n"


def graph_of(text, root="A"):
    """Строит граф из текста тестового репозитория."""
    return build_graph(parse_graph(text), root, 10, "")


class MermaidTest(unittest.TestCase):
    """Проверка вывода Mermaid."""

    def test_simple(self):
        text = to_mermaid(graph_of("A: B\nB:\n"))
        self.assertEqual(
            text,
            'graph TD\n    n0["A"]\n    n1["B"]\n    n0 --> n1',
        )

    def test_quotes_are_escaped(self):
        text = to_mermaid({'a"b': []})
        self.assertIn("a#quot;b", text)

    def test_special_characters_in_names(self):
        text = to_mermaid({"lib-x:1": ["so+2"], "so+2": []})
        self.assertIn('n0["lib-x:1"]', text)
        self.assertIn("n0 --> n1", text)

    def test_cycle_edge_is_kept(self):
        self.assertIn("n2 --> n0", to_mermaid(graph_of(CYCLE)))


class AsciiTreeTest(unittest.TestCase):
    """Проверка вывода ASCII-дерева."""

    def test_tree(self):
        expected = "\n".join([
            "A",
            "├── B",
            "│   └── D",
            "│       └── F",
            "└── C",
            "    ├── D (уже показан)",
            "    └── E",
        ])
        self.assertEqual(to_ascii_tree(graph_of(BASIC), "A"), expected)

    def test_cycle_mark(self):
        expected = "A\n└── B\n    └── C\n        └── A (цикл)"
        self.assertEqual(to_ascii_tree(graph_of(CYCLE), "A"), expected)

    def test_single_package(self):
        self.assertEqual(to_ascii_tree({"A": []}, "A"), "A")


if __name__ == "__main__":
    unittest.main()
