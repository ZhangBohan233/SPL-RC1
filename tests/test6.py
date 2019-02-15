def tcf():
    try:
        return 0
    except ZeroDivisionError:
        return 1
    finally:
        return 2


if __name__ == "__main__":
    print(tcf())
