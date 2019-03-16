class Pointer:
    def __init__(self, id_):
        self.id = id_

    def __str__(self):
        return "p->{}".format(MEMORY.get_instance(self.id))

    def __repr__(self):
        return self.__str__()


class Memory:
    def __init__(self):
        self.count = 1
        self.memory = {0: None}

    # def free(self):
    #     self.count -= 1
    #     self.memory.pop(self.count)

    def allocate(self, instance):
        """
        Allocate an instance to memory and then return the pointer.

        :param instance:
        :return:
        """
        while self.count in self.memory:
            self.count += 1
        self.memory[self.count] = instance
        return self.count

    def get_instance(self, id_):
        return self.memory[id_]

    def point(self, id_: Pointer):
        return self.memory[id_.id]

    def __str__(self):
        lst = [(x, self.memory[x]) for x in self.memory]
        lst.sort(key=lambda k: k[0])
        return "Memory <{}>({}: {})".format(self.count, len(self.memory), lst)


MEMORY = Memory()
