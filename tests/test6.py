def test(a, b=0, c=1, d=2):
    return a + b + c + d


if __name__ == "__main__":
    print(test(1, d=4))
