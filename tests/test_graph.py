"""Тесты построения графа."""
import unittest

from errors import RepoError
from file_repo import parse_graph
from graph import build_graph

BASIC = "A: B C\nB: D\nC: D E\nD: F\nE:\nF:\nG: H\nH:\n"
CYCLE = "A: B\nB: C D\nC: A\nD: D E\nE:\n"


class GraphTest(unittest.TestCase):
    """Проверка build_graph на разных случаях."""

    def test_full_graph(self):
        graph = build_graph(parse_graph(BASIC), "A", 10, "")
        self.assertEqual(
            graph,
            {"A": ["B", "C"], "B": ["D"], "C": ["D", "E"],
             "D": ["F"], "E": [], "F": []},
        )

    def test_unreachable_packages_are_not_included(self):
        graph = build_graph(parse_graph(BASIC), "A", 10, "")
        self.assertNotIn("G", graph)

    def test_bfs_order(self):
        graph = build_graph(parse_graph(BASIC), "A", 10, "")
        self.assertEqual(list(graph), ["A", "B", "C", "D", "E", "F"])

    def test_depth_zero(self):
        graph = build_graph(parse_graph(BASIC), "A", 0, "")
        self.assertEqual(graph, {"A": []})

    def test_depth_one(self):
        graph = build_graph(parse_graph(BASIC), "A", 1, "")
        self.assertEqual(graph, {"A": ["B", "C"], "B": [], "C": []})

    def test_depth_two(self):
        graph = build_graph(parse_graph(BASIC), "A", 2, "")
        self.assertNotIn("F", graph)
        self.assertEqual(graph["D"], [])

    def test_filter(self):
        graph = build_graph(parse_graph(BASIC), "A", 10, "D")
        self.assertNotIn("D", graph)
        self.assertNotIn("F", graph)
        self.assertEqual(graph["B"], [])

    def test_filter_does_not_remove_root(self):
        graph = build_graph(parse_graph(BASIC), "A", 10, "A")
        self.assertIn("A", graph)

    def test_cycle(self):
        graph = build_graph(parse_graph(CYCLE), "A", 10, "")
        self.assertEqual(graph["C"], ["A"])
        self.assertEqual(graph["D"], ["D", "E"])
        self.assertEqual(sorted(graph), ["A", "B", "C", "D", "E"])

    def test_unknown_root(self):
        with self.assertRaises(RepoError):
            build_graph(parse_graph(BASIC), "Z", 3, "")


if __name__ == "__main__":
    unittest.main()
