/*
 * Superclass of
 */
abstract class Iterable {

    function Iterable() {
    }

    /*
     * Returns an object to be iterated.
     */
    abstract function __iter__();

    /*
     * Returns the next iteration.
     */
    abstract function __next__();
}


/*
 * The sign of iteration ends.
 */
class StopIteration {
    function StopIteration() {
    }
}
