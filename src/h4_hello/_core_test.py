from ._core import hello


def test_hello() -> None:
    assert hello() == "Hello!"
