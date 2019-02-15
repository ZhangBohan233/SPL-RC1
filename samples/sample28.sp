def tc(x, y) {
    if (x < 1) {
        return y;
    } else {
        return tc(x - 1, y + 1);
    }
}

tc(600, 750);
