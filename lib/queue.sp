import "stack"
import "iterable"


/*
 * A queue data structure, follows the rule "first in first out".
 */
class Queue {

    function Queue() {
        abstract;
    }

    /*
     * Returns the number of element in this queue.
     */
    function size() {
        abstract;
    }

    /*
     * Adds an element to the last.
     */
    function add_last(element) {
        abstract;
    }

    function remove_last() {
        abstract;
    }

    /*
     * Returns first-added element.
     */
    function get_first() {
        abstract;
    }

    function remove_first() {
        abstract;
    }
}


class Deque extends Queue, Stack {

    function Deque() {
        abstract;
    }

    function add_first(element) {
        abstract;
    }

    function remove_first() {
        abstract;
    }

    function get_last() {
        abstract;
    }

    function remove_last() {
        abstract;
    }
}


class LLNode {
    let before = null;
    let after = null;
    let value = null;
}


class LinkedList extends Deque, Iterable {

    var size_ = 0;
    var head = null;
    var tail = null;

    var iter_node = null;

    function LinkedList() {
    }

    @Override
    function __iter__() {
        iter_node = head;
        return this;
    }

    @Override
    function __next__() {
        if (iter_node) {
            let value = iter_node.value;
            iter_node = iter_node.after;
            return value;
        } else {
            return new StopIteration;
        }
    }

    function __str__() {
        let s = "Link[";
        for (let cur = head; cur; cur = cur.after) {
            s += string(cur.value) + "->";
        }
        s += "]";
        return s;
    }

    @Override
    function size() {
        return size_;
    }

    @Override
    function add_last(element) {
        if (size_ == 0) {
            create(element);
        } else {
            let n = new LLNode;
            n.value = element;
            n.before = tail;
            tail.after = n;
            tail = n;
            size_ += 1;
        }
    }

    @Override
    function add_first(element) {
        if (size_ == 0) {
            create(element);
        } else {
            let n = new LLNode;
            n.value = element;
            n.after = head;
            head.before = n;
            head = n;
            size_ += 1;
        }
    }

    @Override
    function get_last() {
        return tail.value;
    }

    @Override
    function get_first() {
        return head.value;
    }

    @Override
    function remove_first() {
        let n = head;
        head = head.after;
        if (head !== null) {
            head.before = null;
        }
        size_ -= 1;
        return n.value;
    }

    @Override
    function remove_last() {
        let n = tail;
        tail = head.before;
        if (tail) {
            tail.after = null;
        }
        size_ -= 1;
        return n.value;
    }

    @Override
    function top() {
        return get_last();
    }

    @Override
    function pop() {
        return remove_last();
    }

    @Override
    function push(element) {
        return add_last(element)
    }

    function create(ele) {
        let n = new LLNode;
        n.value = ele;
        head = n;
        tail = n;
        size_ = 1;
    }

    function removable() {
        return size_ > 0;
    }
}
