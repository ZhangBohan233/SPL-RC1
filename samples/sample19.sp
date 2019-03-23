def foo(s) {
    if (s < 50) {
        return 0.0;
    } else if (s < 53) {
        return 0.3;
    } else if (s < 57) {
        return 0.6;
    } else if (s < 60) {
        return 1.0;
    } else if (s < 63) {
        return 1.3;
    } else {
        return 4.0;
    }
}

print(foo(60));
