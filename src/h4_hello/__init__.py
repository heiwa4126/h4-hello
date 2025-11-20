from importlib.metadata import version

from ._core import hello

__version__ = version(__package__ or __name__)  # Python 3.9+ only
__all__ = ["hello", "__version__"]
