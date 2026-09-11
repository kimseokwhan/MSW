import sys
sys.stdin = open("binary_search_input.txt")

def binary_search(P, key):
    start = 1
    end = P
    cnt = 0
    while start <= end:
        center = int((start + end) / 2)
        if center == key:
            return cnt
        elif center > key:
            end = center
        else:
            start = center
        cnt += 1
    return -1

T = int(input())
for tc in range(1, T+1):
    P, Pa, Pb = map(int, input().split())

    a = binary_search(P, Pa)
    b = binary_search(P, Pb)

    if a < b:
        print(f'#{tc} A')
    elif a == b:
        print(f'#{tc} 0')
    else:
        print(f'#{tc} B')