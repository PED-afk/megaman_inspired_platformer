



from typing import List


def suggestuion_sort(items: List[str], target: str) -> List[str]:
    def levenshtein_distance(a: str, b: str) -> int:
        a, b = a.lower(), b.lower()
        n, m = len(a), len(b)

        dp = [[0] * (m + 1) for _ in range(n + 1)]

        for i in range(n + 1):
            dp[i][0] = i
        for j in range(m + 1):
            dp[0][j] = j

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                cost = 0 if a[i - 1] == b[j - 1] else 1
                dp[i][j] = min(
                    dp[i - 1][j] + 1,      # deletion
                    dp[i][j - 1] + 1,      # insertion
                    dp[i - 1][j - 1] + cost  # substitution
                )

        return dp[n][m]
    # lower distance = more similar
    return sorted(items, key=lambda x: levenshtein_distance(x, target))