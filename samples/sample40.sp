import "queue"

class Mouse {
    var eat;
    function Mouse(a) {
        eat = a;
    }

    function __str__() {
        return "Mouse" + string(eat);
    }

    function bite() {
        return 121314;
    }
}


class Cat {
    var belly = new LinkedList();

    function eat(mouse) {
        belly.add_last(mouse);
    }

    function __repr__() {
        return "Cat (%r)".format(belly);
    }
}

class Cater {
    var cats;

    function Cater(cats_) {
        cats = cats_;
    }
}

function get(i) {
    return new Mouse(i);
}

if (main()) {
    var arr = new Cat[10];
    for (var i = 0; i < 10; i += 1) {
        arr[i] = new Cat;
        for (var j = 0; j < i; j += 1) {
            arr[i].eat(new Mouse(j));
        }
    }
    println(arr);

    println(memory_view());

    gc();
    println(memory_view());
    //println(arr);

    var g = new Mouse(922);
    println(memory_view());

    var cats = new Cater(arr);
    println(cats.cats);
}