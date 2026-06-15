import yfinance as yf

symbols = [
    "513100.SS",
    "159995.SZ",
    "518880.SS"
]

for s in symbols:
    try:
        df = yf.download(s, period="1mo", auto_adjust=True, progress=False)
        print(s, "rows =", len(df))
    except Exception as e:
        print(s, e)
