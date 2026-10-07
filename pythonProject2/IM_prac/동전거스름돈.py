import sys
sys.stdin = open("동전거스름돈_in.txt")

def change(money, coin):
    global min_cnt
    cnt = 0
    for i in range(1, n+1):
        for j in range(1, n+1):
            a = int(i%j)
            cnt += money // coin[a]
            money = money % coin[a]

    if min_cnt > cnt:
        min_cnt = cnt

T = int(input())
for tc in range(1, T+1):
    m = int(input())
    n = int(input())
    temp = list(map(int, input().split()))
    temp.sort(reverse=True)

    min_cnt = float('inf')
    change(m, temp)

    print(f'#{tc} {min_cnt}')