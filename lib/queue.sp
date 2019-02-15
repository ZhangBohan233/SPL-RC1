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
    before = null;
    after = null;
    value = null;

}


class LinkedList extends Deque, Iterable {

    private size_ = 0;
    private head = null;
    private tail = null;

    private iter_node = null;

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
            value = iter_node.value;
            iter_node = iter_node.after;
            return value;
        } else {
            return new StopIteration;
        }
    }

    function __str__() {
        s = "Link[";
        for (cur = head; cur; cur = cur.after) {
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
            n = new LLNode;
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
            n = new LLNode;
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
        n = head;
        head = head.after;
        if (head !== null) {
            head.before = null;
        }
        size_ -= 1;
        return n.value;
    }

    @Override
    function remove_last() {
        n = tail;
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

    private function create(ele) {
        n = new LLNode;
        n.value = ele;
        head = n;
        tail = n;
        size_ = 1;
    }

    private function removable() {
        return size_ > 0;
    }
}
