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

SPL Key Features:

* Dynamic variables
* Object oriented
* Functional programming
* Slow

### SPL Basic Syntax:

SPL uses braces `{` `}` as block indentation. 

Lines should be terminated by the line terminator `;`.lines with a back brace `}` can have terminator omitted.

SPL uses `//` as one-line comment. In a line, codes after `//` will be ignored by the
interpreter. The `/*` symbol is the beginning of a multi-line comment, where
the `*/` marks the end of the multi-line comment.

#### Variable System:

SPL is a dynamic language. There is no need for declaring the typeof a variable,
but it is necessary to declare the scope level of it.
For example the expression:

`var a = 1;`

declares a var-level variable `a` and sets it to integer 1.

There are 3 types of variables in SPL, which are:

* `var` declares a variable that is accessible in any scope under the scope
where the variable is declared.

* `const` declares a constant that has the same access with the variables
declared by `var`, be once the `const` was declared, it cannot be assigned
again.

### SPL Built-in types:

SPL has several built-in types:

* `int` Integer
* `float` Floating point number
* `boolean` Boolean value, `true` or `false`
* `void` The type name of the `null` pointer
* `string` String literal
* `list` List of any objects
* `pair` Key-value pair
* `set` Set of different objects

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

Notice that the following two code segments
```
function fun() {
    return 1;
}
```
and
```
fun = function () {
    return 1;
}
```
are equivalent. But the first style is recommended for SPL.

### Objects

SPL is object oriented. Objects in SPL are stored in key-value pairs.

#### Class declaration:

SPL uses keyword `class` to specify a class declaration. Attributes of a class
lies directly under the class layer. For example:
```
class Person {
    var name = "unknown";
    var age = 0;
}
```
Class constructor is a method that has same name of that class.
```
class Person {
    var name = "unknown";
    var age = 0;
    function Person(n) {
        name = n;
    }
}
```

Class inheritance uses the keyword `extends`. The subclass has all attributes
and methods of its superclass. SPL supports multiple inheritance, 
separated with comma. But be aware that if there are attributes that has 
same names, the value from the posterior superclass will be inherited.

```
class Student extends Person, Other {
    var grade = 0;
    function Student(n, g) {
        Person(n);
        Other();
        grade = g;
    }
    
    function get() {
        return this;
    }
}
```

SPL allows override. If you defined a method in the subclass which is already
defined in the superclass, you will call the nearest one.

An abstract method can be declared using keyword `abstract`. For example,
```
function foo() {
    abstract;
}
```

The way of overloading operator is to use the keyword `operator`. All binary
operators can be overloaded except id comparators `===`, `!==`, and instance
comparator `instanceof`.

```
class A {
    var value = 0;
    operator +(other) {
        return new A(value + other.value);
    }
}
```

There is a keyword `private` to make a class attribute or method private.
Attributes with private access are not accessible from outer scope, but are
accessible from children classes. But declare an attribute to be private
has no effect on performance.


### Conditional statements

#### If-else statement:

Syntax:
```
if (condition) {
    // If the condition satisfies
} else {
    // Elsewhere, not nessesarily exist
}
```

The condition can be a binary expression with a returning value, 
a `boolean` value, or an object. The following will be interpreted 
as `true`:

* `int` if the integer is not 0
* `float` if the number is not 0.0
* `Object` if the object is not `null`

Note that, nested "if-else" block can be simplified using "else if", 
for example:

```
let num;
if (ch == "a") {
    num = 1;
} else if (ch == "b") {
    num = 2;
} else {
    num = 0;
}
```

#### While loop:

Syntax of while loop is
```
while (condition) {
    ...
}
```
While loop will keep looping until the condition failed once. The condition
block follows the same rule as the if-else statement.

#### For loop:

There are two types of for-loop in SPL. One is the traditional 3-parts
for-loop, which is

```
for (beginning; stop-condition; step) {
    ...
}
```

For example,
```
for (var i = 0; i < 4; i += 1) {
    print(i);
}
```
which will output
```
0
1
2
3
```
Note that, `i += 1` is equivalent to `i = i + 1`.

SPL supports another type of for-loop, which is called for-each loop.
The syntax of for-each loop is:
```
for (var invariant; iterable) {
    ...
}
```
Where the invariant is the loop-invariant, and the iterable is the object
to iterate through. The iterable must either be one of `list`, `set`, 
`pair`, `string`, or extends the abstract class `Iterable`.
