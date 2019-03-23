/*
 * A type of dynamic building strings.
 */
class StringBuilder {

    var lst;
    var len = 0;

    function StringBuilder() {
        lst = list();
    }

    function append(s) {
        var v = string(s);
        len += v.length();
        lst.append(v);
    }

    function to_string() {
        return natives.str_join("", lst);
    }

    function length() {
        return len;
    }

    function substring(from, to=null) {
        return to_string().substring(from, to);
    }

    function __str__() {
        return to_string();
    }
}