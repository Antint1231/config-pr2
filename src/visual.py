"""Текстовое представление графа: Mermaid и ASCII-дерево."""

BRANCH = "├── "
LAST_BRANCH = "└── "
PIPE = "│   "
SPACE = "    "
MARK_CYCLE = " (цикл)"
MARK_SHOWN = " (уже показан)"
QUOTE_CODE = "#quot;"


def escape_label(name):
    """Экранирует кавычки в подписи узла Mermaid."""
    return name.replace('"', QUOTE_CODE)


def to_mermaid(graph):
    """Описывает граф на языке диаграмм Mermaid.

    Каждому пакету дается короткий идентификатор n0, n1, ..., потому что
    в именах пакетов бывают символы (-, :, +), недопустимые в Mermaid.
    """
    ids = {name: f"n{number}" for number, name in enumerate(graph)}
    lines = ["graph TD"]
    for name, node_id in ids.items():
        lines.append(f'    {node_id}["{escape_label(name)}"]')
    for name, dependencies in graph.items():
        for dep in dependencies:
            lines.append(f"    {ids[name]} --> {ids[dep]}")
    return "\n".join(lines)


def get_mark(graph, dep, path, shown):
    """Возвращает пометку для пакета, который не нужно раскрывать."""
    if dep in path:
        return MARK_CYCLE
    if dep in shown and graph[dep]:
        return MARK_SHOWN
    return ""


def add_children(graph, name, prefix, path, shown, lines):
    """Добавляет в lines строки с зависимостями пакета name."""
    dependencies = graph[name]
    for index, dep in enumerate(dependencies):
        is_last = index == len(dependencies) - 1
        mark = get_mark(graph, dep, path, shown)
        branch = LAST_BRANCH if is_last else BRANCH
        lines.append(prefix + branch + dep + mark)
        if dep in path or dep in shown:
            continue
        shown.add(dep)
        path.add(dep)
        child_prefix = prefix + (SPACE if is_last else PIPE)
        add_children(graph, dep, child_prefix, path, shown, lines)
        path.remove(dep)


def to_ascii_tree(graph, root):
    """Рисует зависимости пакета root в виде ASCII-дерева.

    Если пакет уже был показан выше, он повторно не раскрывается, а при
    возврате к предку на пути помечается как цикл.
    """
    lines = [root]
    add_children(graph, root, "", {root}, {root}, lines)
    return "\n".join(lines)
