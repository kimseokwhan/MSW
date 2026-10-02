import sys; sys.stdin = open("quick_sort_input.txt")

T = int(input())
for tc in range(1, T+1):
    N = int(input())
    arr = list(map(int, input().split()))


# # 강사님 풀이
# # Quick_Lomuto 연습
# def lomuto_partition(a, l, r):
#     pivot = a[r]
#     i = l - 1       # 피봇보다 작은 값의 마지막 인덱스
#     for j in range(l, r):
#         if a[j] < pivot:
#             i += 1
#             a[i], a[j] = a[j], a[i]
#     a[i+1], a[r] = a[r], a[i+1]
#     return i+1
#
# def quicksort(a, l, r):
#     if l < r:
#         pivot = lomuto_partition(a, l, r)
#         quicksort(a, l, pivot - 1)
#         quicksort(a, pivot + 1, r)
#
# N = int(input())
# arr = list(map(int, input().split()))
# quicksort(arr, 0, N-1)
# print(arr)