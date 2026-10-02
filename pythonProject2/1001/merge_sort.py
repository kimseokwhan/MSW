import sys; sys.stdin = open("merge_sort_input.txt")

def merge(arr):
    global cnt

    mid = len(arr) // 2
    left = arr[:mid]
    right = arr[mid:]

    merge(left)
    merge(right)

    while 1:
        pass



T = int(input())
for tc in range(1, T+1):
    N = int(input())
    arr = list(map(int, input().split()))

    cnt = 0
    merge(arr)
    print(f'#{tc} {arr[N//2]} {cnt}')





















































# def merge(start, end):
#     global cnt
#     if start == end:
#         return
#     mid = (start + end - 1) // 2
#
#     merge(start, mid)
#     merge(mid + 1, end)
#
#     a = start
#     b = mid + 1
#     result = []
#
#     if arr[mid] > arr[end]:
#         cnt += 1
#
#     while 1:
#         if a > mid and b > end: break
#         if a > mid:
#             result.append(arr[b])
#             b += 1
#         elif b > end:
#             result.append(arr[a])
#             a += 1
#         elif arr[a] <= arr[b]:
#             result.append(arr[a])
#             a += 1
#         else:
#             result.append(arr[b])
#             b += 1
#
#     for i in range(len(result)):
#         arr[start + i] = result[i]
#
# T = int(input())
# for tc in range(1, T+1):
#     N = int(input())
#     arr = list(map(int, input().split()))
#
#     cnt = 0
#     merge(0, N-1)
#     print(f'#{tc} {arr[N//2]} {cnt}')


# 강사님 풀이