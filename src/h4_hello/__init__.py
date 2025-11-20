from ._core import hello
from .__main__ import main
from importlib.metadata import version

__version__ = version(__package__ or __name__)  # Python 3.9+ only
__all__ = ["hello", "main", "__version__"]
