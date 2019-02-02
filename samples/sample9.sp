function test(a) {
    while (a < 100) {
        a = a + 1;
        if (a % 10 == 0) {
            continue;
        }
        print(a);
    }
    return null;
}

c = test(0);
