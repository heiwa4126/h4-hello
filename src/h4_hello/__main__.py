import argparse

from . import __version__
from ._core import hello


def main() -> None:
    parser = argparse.ArgumentParser(
        description="A simple hello world example",
        prog="h4-hello",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s v{__version__}",
    )

    parser.parse_args()
    print(hello())


if __name__ == "__main__":
    main()
