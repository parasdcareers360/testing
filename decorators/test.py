from retry_decorator import retry_

always_fail_count = 0

@retry_(retries=10)
def always_fails():
    global always_fail_count

    always_fail_count += 1
    raise ConnectionError("Payer API is unavailable")


print(always_fails())