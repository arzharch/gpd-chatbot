def should_retry(score: float, retries: int, threshold: float, max_retries: int) -> bool:
    if retries >= max_retries:
        return False
    return score < threshold
