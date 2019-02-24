/*
 * An input stream that reads text file.
 */
class TextInputStream {

    var fp = null;

    function TextInputStream(file_name) {
        fp = f_open(file_name, "r");
    }

    function read() {
        return fp.read();
    }

    function readline() {
        return fp.readline();
    }

    function close() {
        return fp.close();
    }
}


/*
 * An input stream that reads binary file.
 */
class FileInputStream {

    var fp = null;

    function FileInputStream(file_name) {
        fp = f_open(file_name, "rb");
    }

    function read() {
        return fp.read();
    }

    function read_one() {
        return fp.read_one();
    }

    function close() {
        return fp.close();
    }
}


/*
 * An output stream that writes text file.
 */
class TextOutputStream {

    var fp = null;

    function TextOutputStream(file_name) {
        fp = f_open(file_name, "w");
    }

    function write(s) {
        return fp.write(s);
    }

    function flush() {
        return fp.flush();
    }

    function close() {
        return fp.close();
    }
}


/*
 * An output stream that writes binary file.
 */
class FileOutputStream {

    var fp = null;

    function FileOutputStream(file_name) {
        fp = f_open(file_name, "wb");
    }

    function write(s) {
        return fp.write(s);
    }

    function flush() {
        return fp.flush();
    }

    function close() {
        return fp.close();
    }
}
