function con(x) {
    if (x < 100) {
        return true;
    } else {
        return false;
    }
}

function ten(x) {
    return x % 10 == 0;
}

function test(a) {
    while (con(a)) {
        a = a + 1;
        if (ten(a)) {
            continue;
        }
        print(a);
    }
    return null;
}

c = test(0);
