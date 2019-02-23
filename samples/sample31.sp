import "sample28.sp" as s28

class B {
    c = new s28::S28(33);

    i = 0;
    c.set(i);

    print(c.value);
}

b = new B;
