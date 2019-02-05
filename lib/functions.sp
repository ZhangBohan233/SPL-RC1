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


/*  */
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
