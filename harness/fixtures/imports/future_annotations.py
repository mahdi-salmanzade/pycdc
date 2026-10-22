# feature: imports
# summary: from __future__ import annotations turns annotations into strings (must be preserved)
from __future__ import annotations


def f(x: list[int], y: 'Quoted' = None) -> dict[str, Undefined]:
    return x


class Node:
    parent: Node | None
    children: list[Node] = []


def observe():
    return [f.__annotations__, Node.__annotations__, f([1])]
