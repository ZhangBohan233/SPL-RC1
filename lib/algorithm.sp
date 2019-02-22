import "math";


/*
 * Sorts the <lst> with merge sort algorithm.
 */
function merge_sort(lst) {
    length = lst.length();
    step = 1;
    while (step < length) {
        for (i = 0; i < length; i += step * 2) {
            mid = i + step;
            end = mid + step;
            if (end > length) {
                end = length;
            }
            if (mid > length) {
                mid = length;
            }

            c_len = end - i;
            i1 = i;
            i2 = mid;
            ci = 0;
            cache = list();

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
            remain = mid - i1;
            if (remain > 0) {
                for (x = 0; x < remain; x += 1) {
                    cache.append(lst[i1 + x]);
                }
                for (x = 0; x < c_len; x += 1) {
                    lst[i + x] = cache[x];
                }
            } else {
                for (x = 0; x < ci; x += 1) {
                    lst[i + x] = cache[x];
                }
            }
        }
        step *= 2;;
    }
}


/*
 * Returns a list with length <length> containing random integers in range [min, max].
 */
function rand_list(length, min, max) {
    lst = list();
    x = 0;
    r = max - min;
    for (i = 0; i < length; i += 1) {
        x = math.random() * r + min;
        xi = int(x);
        lst.append(xi);
    }
    return lst;
}
