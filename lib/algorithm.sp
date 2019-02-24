import "math";


/*
 * Sorts the <lst> with merge sort algorithm.
 */
function merge_sort(lst) {
    let length = lst.length();
    let step = 1;
    while (step < length) {
        for (let i = 0; i < length; i += step * 2) {
            let mid = i + step;
            let end = mid + step;
            if (end > length) {
                end = length;
            }
            if (mid > length) {
                mid = length;
            }

            let c_len = end - i;
            let i1 = i;
            let i2 = mid;
            let ci = 0;
            let cache = list();

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
            let remain = mid - i1;
            if (remain > 0) {
                for (let x = 0; x < remain; x += 1) {
                    cache.append(lst[i1 + x]);
                }
                for (let x = 0; x < c_len; x += 1) {
                    lst[i + x] = cache[x];
                }
            } else {
                for (let x = 0; x < ci; x += 1) {
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
    let lst = list();
    let x = 0;
    let r = max - min;
    let xi;
    for (let i = 0; i < length; i += 1) {
        x = random() * r + min;
        xi = int(x);
        lst.append(xi);
    }
    return lst;
}
