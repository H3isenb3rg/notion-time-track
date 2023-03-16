from rich.console import Console
from rich.tree import Tree
from rich.markdown import Markdown
from typing import Iterable


console = Console()
print = console.print  # sourcery skip: avoid-builtin-shadow


def print_markdown(string: str, style="none"):
    print(Markdown(string, style=style))


def print_title(raw_title: str):
    print_markdown(f"# {raw_title}")


def print_options_as_tree(title: str, elements: Iterable, add_index: bool = True):
    prompt = Tree(title)
    for i, option in enumerate(elements):
        prompt.add(Markdown(f"{f'{i} &rarr; ' if add_index else ''}{str(option).capitalize()}"))
    print(prompt)
