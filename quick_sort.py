
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    else:
        pivot = arr.pop()
        less = []
        greater = []
        for x in arr:
            if x <= pivot:
                less.append(x)
            else:
                greater.append(x)
        return quicksort(less) + [pivot] + quicksort(greater)

# Пример использования
my_list = [64, 34, 25, 12, 22, 11, 90]
sorted_list = quicksort(my_list.copy())
print("Отсортированный массив:", sorted_list)
