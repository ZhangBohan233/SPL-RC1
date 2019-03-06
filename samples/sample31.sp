import "queue"

println(getcwf());
if (main()) {
    var lst = new LinkedList();
    for (var j = 1; j < 6; j += 1) {
        lst.add_last(j);
    }

    var j = 0;
    while (j < 5) {
        for (var i = 0; i < 10; i += 1) {
            var a = i * j;
            if (i == 2) {
                break;
            }
            println(a);
        }
        if (j == 3) {
            break;
        }
        j += 1;
    }
}
