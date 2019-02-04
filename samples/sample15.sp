import "functions";

a = list(1, 2, 3, 4);

function f(x) {
    return x * 2;
}

lst = map(f, a);  // fuck this
print(lst);
