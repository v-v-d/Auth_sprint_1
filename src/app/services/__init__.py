def test_ci():
    try:
        1/0
    except ZeroDivisionError:
        raise
    return 1
