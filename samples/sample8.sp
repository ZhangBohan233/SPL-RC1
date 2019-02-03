import "algorithm"


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

    operator -(other) {
        return new TypeA(value - other.value);
    }
}

b = new TypeA(4);
c = new TypeA(7);

//d = b.add(c);
d = b - c;
d;
