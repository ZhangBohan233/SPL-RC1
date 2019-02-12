def tcf():
    try:
        return 0
    except ZeroDivisionError:
        return 1
    finally:
        if 0 != 0:
            return


if __name__ == "__main__":
    print(tcf())
