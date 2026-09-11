import sys
sys.stdin = open("special_alignment_input.txt")

T = int(input())
for tc in range(1, T+1):
    N = int(input())
    arr = list(map(int, input().split()))

    # selection(arr)

    # for i in range(N):
    #     pass

    # print(f'#{tc}', end=' ')
    # for i in range(10):
    #     print(arr[i], end=' ')
    # print()
    print(f'#{tc}', *arr[:10])































# 강사님 풀이
def selection(a):
    for i in range(0, 10):
        idx = i     # 최대최소값의 인덱스 찾기
        if i % 2 == 0:  # 최대값의 인덱스
            for j in range(i+1, N):
                if a[idx] < a[j]:
                    idx = j
        else:   # 최소값의 인덱스
            for j in range(i+1, N):
                if a[idx] > a[j]:
                    idx = j
        a[i], a[idx] = a[idx], a[i]
