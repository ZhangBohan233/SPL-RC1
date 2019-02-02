class TypeA {
    value = 0;

    function TypeA(v) {
        value = v;
    }

    function copy() {
        return new TypeA(value);
    }
}


a = new TypeA(3);

b = new TypeA;

b.copy();
