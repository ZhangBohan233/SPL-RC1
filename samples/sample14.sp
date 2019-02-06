//import "sample8.sp";
//import "user/u1.sp";
import "algorithm";

lst = list();

lst = rand_list(100, -32768, 32767);
//print(lst);

st = time();
merge_sort(lst);
end = time();

print(lst);
print(end - st);
