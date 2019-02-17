//import "sample8.sp";
//import "user/u1.sp";
import "algorithm";

lst = list();

print(random());
lst = rand_list(100, -32768, 32767);
print(lst);

st = system.time();
merge_sort(lst);
end = system.time();

//print(lst);
print(end - st);
