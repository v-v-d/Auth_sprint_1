def test_ci():
    try:
        1 / 0 or 2 / 0
    except ZeroDivisionError:
        raise
    return 1


def test_ci2():
    try:
        1 / 0 or 2 / 0
    except ZeroDivisionError:
        raise
    return 1
