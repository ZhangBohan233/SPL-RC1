/*
 * Passes every element from <lst> through the callable <ftn> and returns the collection of
 * results, in the original order.
 */
function map(ftn, lst) {
    res = list();
    for (i = 0; i < lst.length(); i += 1) {
        element = lst[i];
        cal = ftn(element);
        res.append(cal);
    }
    return res;
}


/*
 * Filters elements in <lst> with function <ftn>.
 * Only elements make <ftn> returns <true> will be in the retuning list.
 */
function filter(ftn, lst) {
    res = list();
    for (i = 0; i < lst.length(); i += 1) {
        element = lst[i];
        bool = ftn(element);
        if (bool) {
            res.append(element);
        }
    }
    return res;
}


/*
 * Returns true iff every element in <lst> satisfies boolean function <ftn>.
 */
function all(ftn, lst) {
    for (i = 0; i < lst.length(); i += 1) {
        element = lst[i];
        if (ftn == null) {
            res = element;
        } else {
            res = ftn(element);
        }
        if (!res) {
            return false;
        }
    }
    return true;
}


/*
 * Returns true iff any element in <lst> satisfies boolean function <ftn>.
 */
function any(ftn, lst) {
    for (i = 0; i < lst.length(); i += 1) {
        element = lst[i];
        if (ftn == null) {
            res = element;
        } else {
            res = ftn(element);
        }
        if (res) {
            return true;
        }
    }
    return false;
}
