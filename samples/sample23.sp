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

    def set_grade(g) {
        grade = g;
    }

    def get_grade() {
        return grade;
    }

    operator ==(other) {
        if (other instanceof 'Student') {
            if (name == other.name) {
                return true;
            }
        }
        return false;
    }

    operator !=(other) {
        return this == other;
    }

    function get() {
        return this;
    }

    //function get_name() {
    //    return name;
    //}
}


a = new Student("ta", 1);
print(type(a));
b = new Student("ta", 1);
print(a == b);
print(a != b);
c = b.get();
print(c === a);
