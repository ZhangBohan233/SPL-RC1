class Dog {
    age = 2;

    function older() {
        age = age + 1;
    };
};


class Fuck {
    dog = new Dog;
};

class Sample {
    a = 1;
    b = new Fuck;
    s = "fdg xs//2";

    function set_a(na) {
        a = na;
    };
};


class Extend extends Sample {
    a = 99;
    c = 6;
};


class DoubleExtend extends Extend {
    a = -22.2;
    d = 4;

    function sum() {
        a + b.dog.age + c + d;
    };
};


g = new DoubleExtend;
g.sum();

print(g.s + "333");
print(g.b.dog.age);
a = g.b.dog;
a.older();
print(a.age);
