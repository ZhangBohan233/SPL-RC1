function con(ftn) {
    return ftn();
}

f = con(function () {print(6);});
print(f);
