from rich.console import Console
from rich.tree import Tree
from rich.markdown import Markdown
from typing import Iterable


console = Console()
print = console.print  # sourcery skip: avoid-builtin-shadow


def print_title(raw_title: str):
    print(Markdown(f"# {raw_title}"))


def print_options_as_tree(title: str, elements: Iterable[str]):
    prompt = Tree("What would you like to do?")
    for i, option in enumerate(elements):
        prompt.add(f'{i}->{option.capitalize()}')
    print(prompt)
