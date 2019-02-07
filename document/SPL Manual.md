## **Slowest Programming Language**

###### _Product of Trash Software Studio_

Slowest Programming Language (SPL) is a light-weight scripting language.

SPL focuses on making codes simpler. Here's the general idea: 

* Code should be simple and easy for reading. 
fancy-looking codes somehow shows your programming skills but harmful to readers.
So complicated syntax is not allowed in SPL. There should not be too much code 
in one line.

For these purpose, SPL does not support the following features:

* Multiple line expressions
* Sequential function calls

SPL Key Features:

* Dynamic variables
* Object oriented
* Functional programming
* Slow

### SPL Basic Syntax:

SPL uses braces `{` `}` as block indentation. 

Lines should be terminated by the line terminator `;`.lines with a back brace `}` can have terminator omitted.

SPL is a dynamic language. There is ne need for declaring type when declare a variable.
For example the expression:

`a = 1;`

declares a variable `a` and sets it to integer 1.

### SPL Built-in types:

SPL has several built-in types:

* `int` Integer
* `float` Floating point number
* `string` String literal
* `boolean` Boolean value, `true` or `false`
* `void` The type name of the `null` pointer

### Functions:

#### Function declaration:

SPL allows you to define a function with either `function` or `def` as key word.

The function header is made up by a keyword (`function` or `def`), 
the function name (optional), and the function parameters, quoted with brackets.
The parameters are separated with comma.

Function body is surrounded by braces.

#### Function return value:

Unlike most of the programming languages, SPL functions automatically returns the 
value of the last line executed. A `return` statement just stops a function and
"by the way" returns the value. For example the two following code segment:
```
function foo(a) {
    a;
}
```
and
```
function bar(a) {
    return a;
}
```
are equivalent.

#### Anonymous functions:

SPL allows anonymous function declarations. For example.
```
function (a) {
    return a;
}
```
This kind of syntax is usually used as inner functions.

#### Default argument:
Default value of argument is allowed by writing a `=` after a parameter, 
but it should apply the following rules:

1. No parameter with default argument can be in front of a parameter with NO default value.
2. No expression can be in the default value. In another word, default value can only
be one of names, `int`'s, `float`'s, `string`'s, `boolean`'s, or `null`.

Example:
```
function foo(a, b, c=0, d="a string") {...}
```

#### Function calls:

SPL uses `(` and `)` to identify function calls, just like most of the programming
languages. For example if we have defined our function `foo` as above, then
```
foo(1, 2, 3, "another string");
```
calls the function `foo`, with arguments `1`, `2`, `3`, and `"another string"`.

If we leave parameters with default argument blank like this:
```
foo(1, 2);
```
the parameter `c` will be `0`, `d` will be `"a string"`.

#### Closure:

SPL supports closure.Functions in SPL is a type of object, 
which is stored in the same way as any other
variables. And, the environment of outer function will be stored in the inner
function. This means the following syntax is allowed:
```
function foo(n) {
    function () {
        n = n + 1;
        return n;
    }
}
f = foo(3);
f();
res = f();
print(res);
```
Which will print out an integer value `5`.

Use `=>` symbol for calling the returning function of the last called function.
For example:
```
foo(3)=>();
```
will be equivalent to:
```
f = foo(3);
f();
```
and both of the codes will return `4`;
