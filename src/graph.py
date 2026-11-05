"""Построение графа зависимостей."""
from errors import RepoError


def build_graph(repo, root, max_depth, substring):
    """Строит граф зависимостей пакета обходом в ширину (BFS).

    Результат - словарь «пакет: список его зависимостей». Пакеты, в имени
    которых есть substring, в граф не попадают. Сам корневой пакет
    анализируется всегда. Если max_depth = 1, берутся только прямые
    зависимости, если 0 - только корень.
    """
    if not repo.has_package(root):
        raise RepoError(f"пакет '{root}' не найден в репозитории")
    graph = {root: []}
    bfs_level(repo, [root], 0, max_depth, substring, graph)
    return graph


def is_filtered(name, substring):
    """Нужно ли пропустить пакет из-за фильтра."""
    return bool(substring) and substring in name


def bfs_level(repo, level, depth, max_depth, substring, graph):
    """Обрабатывает один уровень графа и рекурсивно вызывает себя
    для следующего уровня.

    Если пакет уже есть в графе (в том числе при цикле), на него
    добавляется только ребро, а повторно он не обходится.
    """
    if not level or depth >= max_depth:
        return
    next_level = []
    for name in level:
        for dep in repo.dependencies(name):
            if is_filtered(dep, substring):
                continue
            graph[name].append(dep)
            if dep not in graph:
                graph[dep] = []
                next_level.append(dep)
    bfs_level(repo, next_level, depth + 1, max_depth, substring, graph)
