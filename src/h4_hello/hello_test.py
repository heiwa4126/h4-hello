from h4_hello.hello import hello


def test_hello() -> None:
    assert hello() == "Hello!"
