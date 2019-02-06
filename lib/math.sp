function random() {
    m = (1 << 15) - 1;
    a = 3;
    seed = time();
    for (i = 0; i < 100; i += 1) {
        seed = seed * a % m;
    }
    return float(seed) / 32768;
}