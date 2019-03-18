import config_loader as cfg


class Pointer:
    def __init__(self, id_):
        self.id = id_

    def __str__(self):
        return "p->{}".format(MEMORY.get_instance(self.id))

    def __repr__(self):
        return self.__str__()


class Memory:
    def __init__(self):
        self.gc_size = cfg.get_gc_size()
        self.count = 1
        self.memory = {0: None}

    def check_gc(self) -> bool:
        """
        Returns True iff an automatic garbage collection is needed.

        This method returns True if the size of memory exceeds the garbage collection threshold.
        This method should trigger a garbage collection process if True is returned.

        :return: True iff an automatic garbage collection is needed
        """
        return len(self.memory) >= self.gc_size

    def free(self, p: Pointer):
        """
        Frees a pointer.

        Delete the instance stored in the pointer's position.

        :param p: the pointer
        :return: None
        """
        self.memory.pop(p.id)
        self.count = p.id

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
        """
        Returns the instance stored in the position 'id_'.

        :param id_: the position
        :return: the instance stored in the position
        """
        return self.memory[id_]

    def point(self, ptr: Pointer):
        """
        Returns the instance pointed by the pointer.

        :param ptr: the pointer
        :return: the instance pointed by the pointer
        """
        return self.memory[ptr.id]

    def __str__(self):
        lst = [(x, self.memory[x]) for x in self.memory]
        lst.sort(key=lambda k: k[0])
        return "Memory <{}>({}: {})".format(self.count, len(self.memory), lst)


MEMORY = Memory()
