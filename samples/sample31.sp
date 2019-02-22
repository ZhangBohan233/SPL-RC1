import "sample28.sp" as s28


class A {
    x = 0;
    def A(a) {
        x = a;
    }
}

b = new A(1);
print(b);

c = new s28.S28();
print(c);

s28.fuck(6);

print(s28.b);
