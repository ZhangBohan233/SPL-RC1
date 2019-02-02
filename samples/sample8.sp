class TB {
    vv = null;
    vw = 0;

    function TB(va, vb) {
        vv = va;
        vw = vb;
    }
}

class TypeA {
    value = null;
    pre = 5;
    tb = new TB(pre, 9);

    function TypeA(v) {
        value = v;
    }

    function copy() {
        return new TB(value, pre);
    }
}

b = new TypeA(4);

c = b.copy();

d = new TB(7, 5);
