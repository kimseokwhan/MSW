import sys
sys.stdin = open("동전거스름돈_in.txt")

def change(money, coin):    # 완전탐색
    dp = [float('inf')] * (money + 1)   # 배열에 무한대 값(코인 필요 개수)
    dp[0] = 0
    for i in range(1, money+1): # 1원 ~ money원까지
        for j in range(n):      # 동전 돌려가면서 써보기
            if i >= coin[j]:
                dp[i] = min(dp[i], dp[i - coin[j]] + 1)
    return dp[money]

T = int(input())
for tc in range(1, T+1):
    m = int(input())
    n = int(input())
    coin = list(map(int, input().split()))

    ans = change(m, coin)

    print(f'#{tc} {ans}')