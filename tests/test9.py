class Count:

    def __init__(self):
        self.s = 0

    def increment(self):
        self.s += 1


C = Count()
print(id(C))
