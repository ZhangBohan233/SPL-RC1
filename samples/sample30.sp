def printing(func) {
    return def (a, b) {
        print("running");
        func(a, b);
    }
}

def foo(x, y) {
    return x + y;
}

foo = printing(foo);
print(foo(4, 5));
