import asyncio
import datetime
from pyquotex.stable_api import Quotex

EMAIL = "Rakeshrathor792@gmail.com"
PASSWORD = "quotex123"

pairs = [
    "EURUSD_otc", "GBPUSD_otc", "USDJPY_otc",
    "GBPJPY_otc", "EURJPY_otc", "EURGBP_otc",
    "AUDUSD_otc", "NZDUSD_otc", "USDCAD_otc",
    "NZDJPY_otc", "GBPNZD_otc", "CADCHF_otc",
    "AUDNZD_otc", "NZDCHF_otc", "USDINR_otc",
    "USDBRL_otc", "USDMXN_otc", "USDPKR_otc",
    "USDCOP_otc", "USDEGP_otc", "USDPHP_otc",
    "USDARS_otc", "USDIDR_otc", "USDBDT_otc",
    "USDDZD_otc", "USDZAR_otc",
]

def calc_rsi(closes, period=14):
    if len(closes) < period+1:
        return 50
    gains, losses = [], []
    for i in range(1, len(closes)):
        diff = closes[i] - closes[i-1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calc_macd(closes):
    if len(closes) < 26:
        return 0, 0
    ema12 = sum(closes[-12:]) / 12
    ema26 = sum(closes[-26:]) / 26
    macd = ema12 - ema26
    return macd, macd * 0.9

def calc_bb(closes, period=20):
    if len(closes) < period:
        return 0, 0, 0
    sma = sum(closes[-period:]) / period
    std = (sum((x-sma)**2 for x in closes[-period:]) / period) ** 0.5
    return sma + 2*std, sma, sma - 2*std

def analyze(candles):
    if not candles or len(candles) < 5:
        return "WAIT", 0, 50
    closes = [c['close'] for c in candles]
    opens = [c['open'] for c in candles]
    price = closes[-1]
    buy_score = 0
    sell_score = 0
    for i in range(-3, 0):
        if closes[i] > opens[i]: buy_score += 1
        else: sell_score += 1
    rsi = calc_rsi(closes)
    if rsi < 35: buy_score += 2
    elif rsi > 65: sell_score += 2
    elif rsi < 45: buy_score += 1
    elif rsi > 55: sell_score += 1
    macd, signal = calc_macd(closes)
    if macd > signal: buy_score += 2
    else: sell_score += 2
    upper, mid, lower = calc_bb(closes)
    if price < lower: buy_score += 2
    elif price > upper: sell_score += 2
    ema5 = sum(closes[-5:]) / 5
    ema10 = sum(closes[-10:]) / 10 if len(closes) >= 10 else ema5
    if ema5 > ema10: buy_score += 1
    else: sell_score += 1
    if len(closes) >= 3:
        if closes[-1] - closes[-3] > 0: buy_score += 1
        else: sell_score += 1
    total = buy_score + sell_score
    conf = int((max(buy_score, sell_score) / total) * 100)
    if buy_score > sell_score and conf >= 60:
        return "CALL", price, conf
    elif sell_score > buy_score and conf >= 60:
        return "PUT", price, conf
    else:
        return "WAIT", price, conf

async def get_signal(client, pair):
    try:
        candles = await client.get_candles(pair, 60, 30, 60)
        if candles and len(candles) > 0:
            return analyze(candles)
        return "WAIT", 0, 0
    except:
        return "WAIT", 0, 0

async def run():
    while True:
        try:
            client = Quotex(email=EMAIL, password=PASSWORD)
            
            # Safe connect
            try:
                result = await client.connect()
                if result is None:
                    print("Connect returned None - retry in 60s")
                    await asyncio.sleep(60)
                    continue
                check, reason = result
            except Exception as e:
                print(f"Connect error: {e} - retry in 60s")
                await asyncio.sleep(60)
                continue

            if not check:
                print(f"Failed: {reason} - retry in 60s")
                await asyncio.sleep(60)
                continue

            print("✅ Connected!")
            await asyncio.sleep(3)

            while True:
                now = datetime.datetime.now()
                print(f"\n{'='*50}")
                print(f"🕐 {now.strftime('%H:%M:%S')} Scanning...")
                print(f"{'='*50}")

                for pair in pairs:
                    sig, price, conf = await get_signal(client, pair)
                    entry = now.replace(second=0) + datetime.timedelta(minutes=1)
                    expiry = entry + datetime.timedelta(minutes=1)
                    if sig in ["CALL", "PUT"]:
                        icon = "📈" if sig=="CALL" else "📉"
                        print(f"{icon} {pair}: {sig} | {conf}% | {entry.strftime('%H:%M')}-{expiry.strftime('%H:%M')} | {price:.5f}")

                print("⏳ Next scan in 60s...")
                await asyncio.sleep(60)

        except Exception as e:
            print(f"Error: {e} - restart in 30s")
            await asyncio.sleep(30)

asyncio.run(run())
