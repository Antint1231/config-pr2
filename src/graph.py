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
    """Обрабатывает один уровень графа и вызывает себя для следующего.

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


def load_order(graph, root):
    """Возвращает порядок загрузки пакетов для корневого пакета.

    Используется обход в глубину с добавлением пакета в результат после
    всех его зависимостей, поэтому зависимости идут раньше зависящих от
    них пакетов, а сам root - последним. При циклической зависимости
    обратное ребро игнорируется, потому что пакет уже посещен.
    """
    order = []
    visit(graph, root, set(), order)
    return order


def visit(graph, name, seen, order):
    """Рекурсивно обходит зависимости пакета и дополняет order."""
    seen.add(name)
    for dep in graph[name]:
        if dep not in seen:
            visit(graph, dep, seen, order)
    order.append(name)
