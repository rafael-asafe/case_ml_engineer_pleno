from main import hello_word


def test_main():
    response = hello_word()

    assert response == "hello_word!"
