from ._core import goodbye, hello


def test_hello() -> None:
    assert hello() == "Hello!"


def test_goodbye() -> None:
    assert goodbye() == "Goodbye!"
