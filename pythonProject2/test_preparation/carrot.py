# import sys
# sys.stdin = open("carrot_input.txt")

T = int(input())
for tc in range(1, T+1):
    N = int(input())
    C = list(map(int, input().split()))

    cnt = 1
    max_cnt = 1
    for i in range(1, N):
        if C[i] > C[i-1]:
            cnt += 1
            if max_cnt < cnt:
                max_cnt = cnt
        else:
            cnt = 1

    print(f'#{tc} {max_cnt}')