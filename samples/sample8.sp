class TypeA {
    value = 0;

    function TypeA(v) {
        value = v;
    };

    function equals(other) {
        value == other.value;
    };
};


a = new TypeA(3);
av = a.value;

b = new TypeA;
bv = b.value;

t = type(b);
t;
