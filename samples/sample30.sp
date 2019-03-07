import "queue"
import "exception"

var a = new LinkedList();
for (var i = 1; i < 10; i += 1) {
    a.add_last(i);
}

var b;
if (true) {
    b = 2;
} else {
    b = 3;
}

println(b);

for (var i; a) {
    for (var j = 1; j < 10; j += 1) {
        print(j);
        print('*');
        print(i);
        print('=');
        print(i * j);
        print('; ');
        if (j >= i) {
            break;
        }
    }
    println();
}

def ff(g) {
    for (var i = 0; i < 10; i += 1) {
        if (i == 4) {
            return null;
        }
        println(i);
    }
}

println(ff(4));

var x;
try {
    x = 5;
    throw new Exception();
} catch (e: Exception) {
    x = 6;
} finally {
    x = 7;
}

println(x);
