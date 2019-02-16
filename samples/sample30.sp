def printing(func) {
    return def () {
        print("running");
        func();
    }
}

def foo() {
    return 123;
}

foo = printing(foo);
print(foo());
