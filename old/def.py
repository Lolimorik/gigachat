def print_Arr(Arr, elem_end):
    for i in range(0,  elem_end):
        print(Arr[i], end=" ")
    print()


Arr = []
Arr2 = []
for i in range(0,10):
    Arr.append("a"*(i+1))

for i in range(10, 21):
    Arr2.append(i)
    

print_Arr(Arr, 5)
print_Arr(Arr2, 8)

    