import "queue"

a = new LinkedList();

t1 = system.time();
for (i = 0; i < 1000; i+=1) {
    a.add_last(i);
}
for (i = 0; i < 1000; i+=1) {
    a.remove_first();
}
t2 = system.time();

print(t2 - t1);

