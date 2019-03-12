

if (main()) {
    const c = 3;
    const a = pair("a"=1, 2=3, c=5);
    println(a);
    const lst = list(1, 3, 2);
    const d = list(1, 2, list(4, 5), lst[1], "f");
    println(lst);
    println(d);

    println(os.separator);
}