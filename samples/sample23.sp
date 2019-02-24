class Person {
    var name = "unknown";
    var age = 0;
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
    var alive = true;

    def Human() {

    }

    //def die() {
    //    alive = false;
    //}
}

class Creature {
    var molecules = 10000;

    def Creature();

    def die() {
        abstract;
    }
}

class Student extends Person, Human, Creature {
    var grade = 0;
    const v = "STUDENT";
    const g2 = "sb";
    var father = new Human;

    function Student(n, g) {
        Person(n);
        Creature();
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
}


let a = new Student("True", 1);
println(type(a));
let b = new Student("True", 1);
println(a == b);
b.test = function () {print("yyy")};
b.set_grade(2);
println(b.get_grade());
println(dir(Student));
print(b);

