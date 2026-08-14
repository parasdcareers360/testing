from collections import Counter, defaultdict

def smallest_valid_window(logs, suspicious):
    if not logs or not suspicious:
        return (-1, -1)

    need = Counter(suspicious)
    window = defaultdict(int)

    required = len(need)
    formed = 0

    left = 0
    best_len = float('inf')
    best_range = (-1, -1)

    for right, user in enumerate(logs):
        if user in need:
            window[user] += 1
            if window[user] == need[user]:
                formed += 1

        while formed == required:
            current_len = right - left + 1

            if current_len < best_len or (
                current_len == best_len and left < best_range[0]
            ):
                best_len = current_len
                best_range = (left, right)

            left_user = logs[left]
            if left_user in need:
                window[left_user] -= 1
                if window[left_user] < need[left_user]:
                    formed -= 1
            left += 1

    return best_range


logs = ["A12", "B55", "C11", "A12", "D20", "C11", "E90", "B55", "D20", "C11"]
suspicious = ["A12", "B55", "C11"]

a = smallest_valid_window(logs, suspicious)

print(a)