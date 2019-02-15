/*
 * Superclass of
 */
class Iterable {

    function Iterable() {
        abstract;
    }

    /*
     * Returns an object to be iterated.
     */
    function __iter__() {
        abstract;
    }

    /*
     * Returns the next iteration.
     */
    function __next__() {
        abstract;
    }
}


/*
 * The sign of iteration ends.
 */
class StopIteration {
    function StopIteration() {
    }
}
