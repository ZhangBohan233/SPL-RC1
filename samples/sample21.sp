import "io";

a = new FileInputStream("tests/t.txt");
s = a.read_one();
while (s != null) {
    print(s);
    s = a.read_one();
}
a.close();

b = new TextOutputStream("tests/t2.txt");
b.write("asdfg");
b.flush();
b.close();

