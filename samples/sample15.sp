import "functions";

let a = list(1, 2, 3, 4);

let r = reduce(function (x, y) {x + y}, a);
println(r);

println(sum(list(7, 8, 2, 3, 6)));

println(all(null, list()));
