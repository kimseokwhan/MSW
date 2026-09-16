import sys
sys.stdin = open("im_input.txt")

T = int(input())
for tc in range(1, T+1):
    N, S = map(int, input().split())
    arr = sorted(list(map(int, input().split())))

    

    print(f'#{tc} {ans}')