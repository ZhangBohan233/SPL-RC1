class Person {
    name = "unknown";
    age = 0;
    function Person(n) {
        name = n;
    }

    //function __str__() {
    //    return "asd";
    //}

    function get_name() {
        return "gg";
    }
}

class Human {
    alive = true;

    def die() {
        alive = false;
    }
}

class Creature {
    molecules = 10000;

    def die() {
        abstract;
    }
}

class Student extends Person, Human, Creature {
    private grade = 0;
    const v = "STUDENT";
    private const g2 = "sb";
    father = new Human;

    function Student(n, g) {
        Person(n);
        age = g + 18;
        grade = g;
    }

    def die() {
        alive = false;
        molecules = 1;
    }

    def test() {
        print("xxx");
    }

    const def access() {
        test();
    }

    def set_grade(g) {
        grade = g;
    }

    def get_grade() {
        return grade;
    }

    operator ==(other) {
        return other instanceof Student && other.name == name;
    }

    operator !=(other) {
        return !(this == other);
    }

    function get() {
        return this;
    }

    //function get_name() {
    //    return name;
    //}
}


a = new Student("True", 1);
print(type(a));
b = new Student("True", 1);
print(a == b);
b.test = function () {print("yyy")};
b.set_grade(2);
print(b.get_grade())
print(dir(Student));
//print(b);

