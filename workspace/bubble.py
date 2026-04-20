def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

if __name__ == "__main__":
    sample_data = [64, 34, 25, 12, 22, 11, 90]
    print(f"Original array: {sample_data}")
    sorted_data = bubble_sort(sample_data)
    print(f"Sorted array: {sorted_data}")

    test_cases = [
        [5, 1, 4, 2, 8],
        [3, 0, 2, 5, -1, 4, 1],
        [],
        [1]
    ]

    for case in test_cases:
        print(f"Sorting {case} -> {bubble_sort(case[:])}")