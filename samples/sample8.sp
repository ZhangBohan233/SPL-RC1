//import "algorithm"

class TypeA {
    value = null;

    function TypeA(v) {
        value = v;
    }

    function add(other) {
        return new TypeA(value - other.value);
    }

    function fuck(x = "shit") {
        return x;
    }
}

b = new TypeA(4);
c = new TypeA(7);

print(type(c.fuck()));

//d = b.add(c);
//d = b - c;
//d;
