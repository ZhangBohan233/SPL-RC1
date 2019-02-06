import "functions";

a = list(1, 2, 3, 4);
b = list(false, false, false);

function f(x, z = null) {
    return x * 2;
}

function g(x) {
    return x % 2 == 0;
}

lst = map(f, a);  // fuck this
print(lst);

r = any(g, a);
print(r);
print(type(1));

e = any(null, b);
print(e);
