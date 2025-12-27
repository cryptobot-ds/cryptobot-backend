def make_decision(predicted_price: float, last_price: float, threshold: float = 0.01) -> str:
    """
    Retourne BUY / SELL / HOLD selon la variation relative.
    """
    variation = (predicted_price - last_price) / last_price

    if variation > threshold:
        return "BUY"
    elif variation < -threshold:
        return "SELL"
    return "HOLD"