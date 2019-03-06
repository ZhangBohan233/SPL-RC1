function recursion(x) {
    if (x > 1) {
        return recursion(x - 1);
    } else {
        return 1;
    }
}

println(recursion (6));
