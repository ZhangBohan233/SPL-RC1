import "functions"


/*
 * Returns a random `float` number between <0> and <1>.
 */
function random() {
    const m = (1 << 15) - 1;
    const a = 3;
    var seed = system.time();
    for (var i = 0; i < 100; i += 1) {
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
    var x = int(n);
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
    var x = float(n);
    var g = x;
    while (abs(g * g - x) > 0.000001) {
        g = (g + x / g) / 2;
    }
    return g;
}


/*
 * Returns the nearest integer of number <n>.
 */
function round(n) {
    var fl = floor(n);
    var ce = ceil(n);
    var low = n - fl;
    var up = ce - n;
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
    var lim = ceil(sqrt(p));
    if (p == 2) {
        return true;
    } else if (p % 2 == 0) {
        return false;
    } else {
        for (factor = 3; factor < lim; factor += 2) {
            if (p % factor == 0) {
                return false;
            }
        }
        return true;
    }
}


/*
 * Returns a list of primes that less than or equal to <limit>.
 */
function primes(limit) {
    var lst = list();
    for (var i = 2; i <= limit; i += 1) {
        lst.append(i);
    }
    var index = 0;
    var tar = lst[0];
    while (lst[lst.length() - 1] > tar * tar) {
        tar = lst[index];
        lst = filter(function (x) {x == tar || x % tar != 0}, lst);
        index += 1;
    }
    return lst;
}


/*
 * Returns the prime factorization of integer <n>.
 */
function factorization(n) {
    var x = n;
    var ps = primes(n);
    var res = pair();
    if (ps[ps.length() - 1] == n) {
        res[n] = 1;
        return res;
    }
    while (x > 1) {
        for (var p; ps) {
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


function fib(n) {
    if (n < 2) return n;
    else return fib(n - 1) + fib(n - 2);
}
