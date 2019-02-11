/*
 * Returns a random `float` number between <0> and <1>.
 */
function random() {
    m = (1 << 15) - 1;
    a = 3;
    seed = system.time();
    for (i = 0; i < 100; i += 1) {
        seed = seed * a % m;
    }
    return float(seed) / 32768;
}


/*
 * Returns the absolute value of <n>.
 */
function abs(n) {
    if (n >= 0) {
        return n;
    } else {
        return -n;
    }
}


function ceil(n) {
    x = int(n);
    if (n > x) {
        return x + 1;
    } else {
        return x;
    }
}


function floor(n) {
    return int(n);
}


/*
 * Returns the square root of <n>.
 */
function sqrt(n) {
    x = float(n);
    g = x;
    while (abs(g * g - x) > 0.000001) {
        g = (g + x / g) / 2;
    }
    return g;
}


/*
 * Returns the nearest integer of number <n>.
 */
function round(n) {
    fl = floor(n);
    ce = ceil(n);
    low = n - fl;
    up = ce - n;
    if (up > low) {
        return fl;
    } else {
        return ce;
    }
}


/*
 * Returns <true> if <p> is a prime.
 */
function is_prime(p) {
    lim = ceil(sqrt(p));
    for (factor = 2; factor < lim; factor += 1) {
        if (p % factor == 0) {
            return false;
        }
    }
    return true;
}


/*
 * Returns a list of primes that less than or equal to <limit>.
 */
function primes(limit) {
    lst = list();
    for (i = 2; i <= limit; i += 1) {
        if (is_prime(i)) {
            lst.append(i);
        }
    }
    return lst;
}


/*
 * Returns the prime factorization of integer <n>.
 */
function factorization(n) {
    x = n;
    ps = primes(n);
    res = pair();
    if (ps[ps.length() - 1] == n) {
        res[n] = 1;
        return res;
    }
    while (x > 1) {
        for (i = 0; i < ps.length(); i += 1) {
            p = ps[i];
            if (x % p == 0) {
                x /= p;
                if (res.contains(p)) {
                    res[p] = res[p] + 1;
                } else {
                    res[p] = 1;
                }
                break;
            }
        }
    }
    return res;
}
