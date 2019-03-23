import "functions";

class Ca {
    lst = list(1, 2, 3);
}

a = new Ca;

a.lst.append(4);
a.lst[a.lst[1]] = a.lst[3];
a.lst[1];
print(a.lst);
print(all(null, a.lst));
