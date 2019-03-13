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

function get(i) {
    return new Mouse(i);
}

if (main()) {
    var arr = new Mouse[10];
    for (var i = 0; i < 10; i += 1) {
        arr[i] = get(i);
    }
    println(arr);

    println(memory_view());

    gc();
    println(memory_view());
    println(arr);
}