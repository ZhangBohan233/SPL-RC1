import "functions";

a = list(1, 2, 3, 4);

function f(x) {
    return x * 2;
}

function g(x) {
    return x % 2 == 0;
}

lst = map(f, a);  // fuck this
print(lst);

lst = filter(g, a);
print(lst);
