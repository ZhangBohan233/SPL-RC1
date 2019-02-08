class Person {
    name = "unknown";
    age = 0;
    function Person(n) {
        name = n;
    }

    function get_name() {
        return "gg";
    }
}


class Student extends Person {
    grade = 0;
    function Student(n, g) {
        Person(n);
        age = g + 18;
        grade = g;
    }

    //function get_name() {
    //    return name;
    //}
}


a = new Student("ta", 1);
print(a.get_name());
