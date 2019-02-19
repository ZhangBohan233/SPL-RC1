class A:
    child = 3

    def __init__(self, b):
        pass
        # self.child = b
        # type(self).child = b

    # def p(self):
    #     return self.child


class B(A):
    def __init__(self):
        # A.__init__(self, 1)
        pass

    def b(self):
        return self.child


if __name__ == "__main__":
    a = B()
    print(a.b())
