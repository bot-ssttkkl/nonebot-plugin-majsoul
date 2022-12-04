def percentile_str(x: float, ndigits: int = 2) -> str:
    return f'{round(x * 100, ndigits)}%'
