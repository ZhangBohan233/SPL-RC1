import "queue"
import "exception"

let a = new LinkedList();
for (let i = 1; i < 10; i += 1) {
    a.add_last(i);
}

let b;
if (true) {
    b = 2;
} else {
    b = 3;
}

println(b);

for (let i; a) {
    for (let j = 1; j < 10; j += 1) {
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

def ff(a) {
    for (let i = 0; i < 10; i += 1) {
        if (i == 4) {
            return null;
        }
        println(i);
    }
}

println(ff(4));

let x;
try {
    x = 5;
    throw new Exception();
} catch (e: Exception) {
    x = 6;
} finally {
    x = 7;
}

println(x);
