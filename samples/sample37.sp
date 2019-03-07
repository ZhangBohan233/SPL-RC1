import "functions"

var ll = list(1, 2, 3, 4);

function ff(a) {
    return a == 3;
}

if (any(function (a) {return a == 3;}, ll)) {
    println(111);
}
