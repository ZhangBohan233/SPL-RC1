import "queue"

lst = list(0, 1, 2, 3, 4);
for (x; lst) {
    if (x == 1) {
        continue;
    }
    print(x);
    if (x == 3) {
        break;
    }
}


a = new LinkedList();
for (i = 0; i < 10; i+=1) {
    a.add_last(i);
}
for (x; a) {
    print(x);
}
for (x; a) {
    print(100 + x);
}
