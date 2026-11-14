"""Тесты построения графа."""
import unittest

from errors import RepoError
from file_repo import parse_graph
from graph import build_graph, load_order

BASIC = "A: B C\nB: D\nC: D E\nD: F\nE:\nF:\nG: H\nH:\n"
CYCLE = "A: B\nB: C D\nC: A\nD: D E\nE:\n"


class GraphTest(unittest.TestCase):
    """Проверка build_graph на разных случаях."""

    def test_full_graph(self):
        graph = build_graph(parse_graph(BASIC), "A", 10, "")
        self.assert_equal(
            graph,
            {"A": ["B", "C"], "B": ["D"], "C": ["D", "E"],
             "D": ["F"], "E": [], "F": []},
        )

    def test_unreachable_packages_are_not_included(self):
        graph = build_graph(parse_graph(BASIC), "A", 10, "")
        self.assert_not_in("G", graph)

    def test_bfs_order(self):
        graph = build_graph(parse_graph(BASIC), "A", 10, "")
        self.assert_equal(list(graph), ["A", "B", "C", "D", "E", "F"])

    def test_depth_zero(self):
        graph = build_graph(parse_graph(BASIC), "A", 0, "")
        self.assert_equal(graph, {"A": []})

    def test_depth_one(self):
        graph = build_graph(parse_graph(BASIC), "A", 1, "")
        self.assert_equal(graph, {"A": ["B", "C"], "B": [], "C": []})

    def test_depth_two(self):
        graph = build_graph(parse_graph(BASIC), "A", 2, "")
        self.assert_not_in("F", graph)
        self.assert_equal(graph["D"], [])

    def test_filter(self):
        graph = build_graph(parse_graph(BASIC), "A", 10, "D")
        self.assert_not_in("D", graph)
        self.assert_not_in("F", graph)
        self.assert_equal(graph["B"], [])

    def test_filter_does_not_remove_root(self):
        graph = build_graph(parse_graph(BASIC), "A", 10, "A")
        self.assert_in("A", graph)

    def test_cycle(self):
        graph = build_graph(parse_graph(CYCLE), "A", 10, "")
        self.assert_equal(graph["C"], ["A"])
        self.assert_equal(graph["D"], ["D", "E"])
        self.assert_equal(sorted(graph), ["A", "B", "C", "D", "E"])

    def test_unknown_root(self):
        with self.assert_raises(RepoError):
            build_graph(parse_graph(BASIC), "Z", 3, "")


class LoadOrderTest(unittest.TestCase):
    """Проверка порядка загрузки."""

    def order(self, text, root, depth=10, substring=""):
        """Строит граф и возвращает порядок загрузки."""
        graph = build_graph(parse_graph(text), root, depth, substring)
        return load_order(graph, root)

    def test_dependencies_come_first(self):
        order = self.order(BASIC, "A")
        self.assert_equal(order, ["F", "D", "B", "E", "C", "A"])

    def test_every_dependency_before_dependent(self):
        graph = build_graph(parse_graph(BASIC), "A", 10, "")
        order = load_order(graph, "A")
        for name, dependencies in graph.items():
            for dep in dependencies:
                self.assertLess(order.index(dep), order.index(name))

    def test_no_duplicates(self):
        order = self.order(BASIC, "A")
        self.assert_equal(len(order), len(set(order)))

    def test_cycle(self):
        order = self.order(CYCLE, "A")
        self.assert_equal(order, ["C", "E", "D", "B", "A"])

    def test_single_package(self):
        self.assert_equal(self.order(BASIC, "F"), ["F"])

    def test_respects_depth(self):
        self.assert_equal(self.order(BASIC, "A", depth=1), ["B", "C", "A"])


if __name__ == "__main__":
    unittest.main()
