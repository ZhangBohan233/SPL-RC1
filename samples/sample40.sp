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

if (main()) {
    var arr = new Mouse[10];
    for (var i = 0; i < 10; i += 1) {
        arr[i] = new Mouse(i);
    }
    println(arr);
    var bar = new boolean[10];

    bar[1] = true;

    var ll = new LinkedList();
    for (var i = 0; i < 10; i += 1) {
        ll.add_last(i + 20);
    }

    println(memory_view());

    gc();
    println(memory_view());
    println(arr[7].bite());
}