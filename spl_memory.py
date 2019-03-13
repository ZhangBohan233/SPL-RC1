class Memory:
    def __init__(self):
        self.count = 0
        self.memory = {}

    def decrement(self):
        self.count -= 1
        self.memory.pop(self.count)

    def get_and_increment(self, instance):
        """
        Get the current counter id and then add the new instance to memory.

        :param instance:
        :return:
        """
        self.memory[self.count] = instance
        temp = self.count
        self.count += 1
        return temp

    def get_instance(self, id_):
        return self.memory[id_]

    def __str__(self):
        return "Memory({}: {})".format(self.count, self.memory)


# class Pointer:
#     def __init__(self, id_):
#         self.id = id_
#
#     def __str__(self):
#         return "p->{}".format(MEMORY.get_instance(self.id))
#
#     def __repr__(self):
#         return self.__str__()


MEMORY = Memory()
MEMORY.get_and_increment(None)  # null pointer
