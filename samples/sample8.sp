//import "algorithm"

class TypeA {
    value = null;

    function TypeA(v) {
        value = v;
    }

    function add(other) {
        return new TypeA(value - other.value);
    }

    function fuck(x) {
        return function () {
            return x * 2;
        }
    }
}

b = new TypeA(4);
c = new TypeA(7);

print(type(c.fuck(2)));

d = c.fuck(3)=>();
print(d);
