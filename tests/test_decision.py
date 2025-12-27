from ml.utils.decision import make_decision

def test_buy_decision():
    assert make_decision(predicted_price=110, last_price=100) == "BUY"

def test_sell_decision():
    assert make_decision(predicted_price=90, last_price=100) == "SELL"

def test_hold_decision():
    assert make_decision(predicted_price=100.5, last_price=100, threshold=0.01) == "HOLD"
