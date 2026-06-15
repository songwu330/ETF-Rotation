import os
import smtplib
import yfinance as yf
import pandas as pd

from email.mime.text import MIMEText
from email.header import Header

EMAIL_USER = os.environ["EMAIL_USER"]
EMAIL_PASS = os.environ["EMAIL_PASS"]

ASSETS = {
    "纳指ETF": "513100.SS",
    "芯片ETF": "159995.SZ",
    "黄金ETF": "518880.SS"
}

BUFFER = 1.05

results = []

for name, ticker in ASSETS.items():

    df = yf.download(
        ticker,
        period="1y",
        auto_adjust=True,
        progress=False
    )

    close = df["Close"]

    if len(close) < 121:
        continue

    p0 = close.iloc[-1]

    m23 = p0 / close.iloc[-24] - 1
    m20 = p0 / close.iloc[-21] - 1
    m60 = p0 / close.iloc[-61] - 1
    m120 = p0 / close.iloc[-121] - 1

    score = (
        m23 * 0.30 +
        m20 * 0.20 +
        m60 * 0.30 +
        m120 * 0.20
    )

    ma120 = close.tail(120).mean()

    results.append({
        "name": name,
        "ticker": ticker,
        "price": float(p0),
        "score": float(score),
        "ma120": float(ma120),
        "above_ma": p0 > ma120
    })

risk_assets = [
    x for x in results
    if x["name"] != "黄金ETF"
    and x["above_ma"]
]

if risk_assets:

    risk_assets.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    winner = risk_assets[0]

else:

    winner = next(
        x for x in results
        if x["name"] == "黄金ETF"
    )

report = []

report.append("ETF轮动系统 V7.0")
report.append("")
report.append("======评分======")

for r in sorted(
    results,
    key=lambda x: x["score"],
    reverse=True
):

    report.append(
        f"{r['name']} | "
        f"评分={r['score']:.2%} | "
        f"价格={r['price']:.3f} | "
        f"MA120={r['ma120']:.3f} | "
        f"{'强势' if r['above_ma'] else '弱势'}"
    )

report.append("")
report.append("======结论======")
report.append(f"当前冠军ETF：{winner['name']}")
report.append(f"代码：{winner['ticker']}")
report.append("")
report.append("建议：")
report.append(f"持有 {winner['name']}")

content = "\n".join(report)

msg = MIMEText(content, "plain", "utf-8")

msg["Subject"] = Header(
    f"ETF轮动结果：{winner['name']}",
    "utf-8"
)

msg["From"] = EMAIL_USER
msg["To"] = "979249918@qq.com"

server = smtplib.SMTP_SSL(
    "smtp.qq.com",
    465
)

server.login(
    EMAIL_USER,
    EMAIL_PASS
)

server.sendmail(
    EMAIL_USER,
    ["979249918@qq.com"],
    msg.as_string()
)

server.quit()

print(content)
