import "math";


/*
 * Sorts the <lst> with merge sort algorithm.
 */
function merge_sort(lst) {
    const length = lst.length();
    var step = 1;
    while (step < length) {
        for (var i = 0; i < length; i += step * 2) {
            var mid = i + step;
            var end = mid + step;
            if (end > length) {
                end = length;
            }
            if (mid > length) {
                mid = length;
            }

            var c_len = end - i;
            var i1 = i;
            var i2 = mid;
            var ci = 0;
            var cache = list();

            while (i1 < mid && i2 < end) {
                if (lst[i1] < lst[i2]) {
                    cache.append(lst[i1]);
                    ci += 1;
                    i1 += 1;
                } else {
                    cache.append(lst[i2]);
                    ci += 1;
                    i2 += 1;
                }
            }
            var remain = mid - i1;
            if (remain > 0) {
                for (var x = 0; x < remain; x += 1) {
                    cache.append(lst[i1 + x]);
                }
                for (var x = 0; x < c_len; x += 1) {
                    lst[i + x] = cache[x];
                }
            } else {
                for (var x = 0; x < ci; x += 1) {
                    lst[i + x] = cache[x];
                }
            }
        }
        step *= 2;
    }
}


/*
 * Returns a list with length <length> containing random integers in range [min, max].
 */
function rand_list(length, min, max) {
    var lst = list();
    var x = 0;
    var r = max - min;
    var xi;
    for (var i = 0; i < length; i += 1) {
        x = random() * r + min;
        xi = int(x);
        lst.append(xi);
    }
    return lst;
}
