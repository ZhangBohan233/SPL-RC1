/*
 * Superclass of all spl exceptions.
 */
class Exception {
    message = "";

    /*
     * Create a new <Exception>, with message <msg>.
     */
    function Exception(msg="") {
        message = msg;
    }
}