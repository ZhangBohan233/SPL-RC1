def tc(x, y) {
    if (x < 1) {
        return false;
    } else {
        return tc(x - 1, y + 1);
    }
}

tc(600, 2750);
