import "sample28.sp" as s28


class A {
    x = 0;
    def A(a) {
        x = a;
    }
}

def func() {
    return 3;
}

c = new s28::S28(new A(3));
print(c);

s28::fuck(6);

print(new s28::iterable::StopIteration());

//print(s28::c);
