import "queue"

println(getcwf());
if (main()) {
    let lst = new LinkedList();
    for (let j = 1; j < 6; j += 1) {
        lst.add_last(j);
    }

    let j = 0;
    while (j < 5) {
        for (let i = 0; i < 10; i += 1) {
            let a = i * j;
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
