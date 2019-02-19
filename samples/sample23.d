class Person {
    name = "unknown";
    age = 0;
    function Person(n) {
        name = n;
    };
    function get_name() {
        return "gg";
    };
};
class Human {
    alive = true;
    function die() {
        alive = false;
    };
};
class Creature {
    molecules = 10000;
    function die() {
        abstract;
    };
};
class Student extends Person, Human, Creature {
    private grade = 0;
    const v = "STUDENT";
    const private g2 = "sb";
    father = new Human;
    function Student(n, g) {
        Person(n);
        age = g + 18;
        grade = g;
    };
    function die() {
        alive = false;
        molecules = 1;
    };
    const private function test() {
        print("xxx");
    };
    const function access() {
        test();
    };
    function set_grade(g) {
        grade = g;
    };
    function get_grade() {
        return grade;
    };
    function @eq(other) {
        return other instanceof Student && other.name == name;
    };
    function @neq(other) {
        return ! (this == other);
    };
    function get() {
        return this;
    };
};
a = new Student("True", 1);
print(type(a));
b = new Student("True", 1);
print(a == b);
b.access();
print(dir(Student));
