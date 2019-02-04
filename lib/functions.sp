/*
 * Passes every element from <lst> through the callable <ftn> and returns the collection of
 * results, in the original order.
 */
function map(ftn, lst) {
    res = list();
    i = 0;
    while (i < lst.length()) {
        element = lst[i];
        cal = ftn(element);
        res.append(cal);
        i += 1;
    }
    return res;
}


/*  */
function filter(ftn, lst) {
    res = list();
    i = 0;
    while (i < lst.length()) {
        element = lst[i];
        bool = ftn(element);
        if (bool) {
            res.append(element);
        }
        i += 1;
    }
    return res;
}
