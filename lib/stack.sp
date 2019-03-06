/*
 * A stack data structure, follows the rule "last in first out".
 */
abstract class Stack {

    @Suppress
    abstract function size();

    abstract function top();

    abstract function push(element);

    abstract function pop();
}
