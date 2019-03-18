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

abstract class Human {
    var alive = true;

    def Human();

    //def die() {
    //    alive = false;
    //}
}

abstract class Creature {
    var molecules;

    function Creature() {
         molecules = 10000;
    }

    abstract function die();
}

class Student extends Person, Human, Creature {
    var grade = 0;
    const v = "STUDENT";
    const g2 = "sb";
    //var father = new Human;

    function Student(n, grade) {
        Person(n);
        Creature();
        age = grade + 18;
        this.grade = grade;
    }

    @Override
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


var a = new Student("True", 1);
println(type(a));
var b = new Student("True", 1);
println(a == b);
//println(dir(Student));
println(b);

