import sys
sys.stdin = open("스위치조작_in.txt")

def switch(arr1, arr2):
    global ans
    if arr1 == arr2:
        return
    for i in range(N):
        if arr1[i] != arr2[i]:
            for j in range(i, N):
                if arr1[j] == 1:
                    arr1[j] = 0

                else:
                    arr1[j] = 1
            ans += 1

T = int(input())
for tc in range(1, T+1):
    N = int(input())
    arr1 = list(map(int, input().split()))
    arr2 = list(map(int, input().split()))

    ans = 0
    switch(arr1, arr2)
    print(f'#{tc} {ans}')