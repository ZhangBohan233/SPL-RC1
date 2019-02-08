plus_x = def (x) {
    return def (y) {
        return y + x;
    }
}

def mul_x(x) {
    return def (y) {
        return y * x;
    }
}

c = mul_x(plus_x(2)=>(4))=>(3);
print(c);  // 18

a = def () {
    return 1;
}
print(a());
