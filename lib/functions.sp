/*
 * Passes every element from <lst> through the callable <ftn> and returns the collection of
 * results, in the original order.
 */
function map(ftn, lst) {
    var res = list();
    for (var element; lst) {
        var cal = ftn(element);
        res.append(cal);
    }
    return res;
}


/*
 * Filters elements in <lst> with function <ftn>.
 * Only elements make <ftn> returns <true> will be in the retuning list.
 */
function filter(ftn, lst) {
    var res = list();
    for (var element; lst) {
        var bool = ftn(element);
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
    for (var element; lst) {
        var res;
        if (ftn === null) {
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
    for (var element; lst) {
        var res;
        if (ftn === null) {
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


/*
 * Performs the same operation to every element until it went into one.
 */
function reduce(ftn, lst) {
    var result = null;
    for (var element; lst) {
        if (result) {
            result = ftn(result, element);
        } else {
            result = element;
        }
    }
    return result;
}


/*
 * Returns the sum of a list.
 */
function sum(lst) {
    return reduce(function (x, y) {x + y}, lst);
}
