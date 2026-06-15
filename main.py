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

results = []

for name, ticker in ASSETS.items():

    try:

        df = yf.download(
            ticker,
            period="1y",
            auto_adjust=True,
            progress=False
        )

        if df.empty:
            print(f"{ticker} 无数据")
            continue

        close = df["Close"].squeeze()

        if len(close) < 121:
            print(f"{ticker} 数据不足")
            continue

        p0 = float(close.iloc[-1])

        p23 = float(close.iloc[-24])
        p20 = float(close.iloc[-21])
        p60 = float(close.iloc[-61])
        p120 = float(close.iloc[-121])

        m23 = p0 / p23 - 1
        m20 = p0 / p20 - 1
        m60 = p0 / p60 - 1
        m120 = p0 / p120 - 1

        score = (
            m23 * 0.30 +
            m20 * 0.20 +
            m60 * 0.30 +
            m120 * 0.20
        )

        ma120 = float(close.tail(120).mean())

        results.append({
            "name": name,
            "ticker": ticker,
            "price": p0,
            "score": score,
            "ma120": ma120,
            "above_ma": p0 > ma120
        })

    except Exception as e:

        print(f"{ticker} 出错: {e}")

if len(results) == 0:
    raise Exception("所有ETF均未获取到数据")

risk_assets = []

for x in results:

    if (
        x["name"] != "黄金ETF"
        and x["above_ma"]
    ):
        risk_assets.append(x)

if len(risk_assets) > 0:

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
report.append("========== 排名 ==========")

ranking = sorted(
    results,
    key=lambda x: x["score"],
    reverse=True
)

for r in ranking:

    trend = "强势" if r["above_ma"] else "弱势"

    report.append(
        f"{r['name']} | "
        f"评分={r['score']:.2%} | "
        f"价格={r['price']:.3f} | "
        f"MA120={r['ma120']:.3f} | "
        f"{trend}"
    )

report.append("")
report.append("========== 结果 ==========")
report.append("")
report.append(f"冠军ETF：{winner['name']}")
report.append(f"代码：{winner['ticker']}")
report.append("")
report.append(f"建议持有：{winner['name']}")
report.append("")
report.append("规则：")
report.append("23日动量×30%")
report.append("20日动量×20%")
report.append("60日动量×30%")
report.append("120日动量×20%")
report.append("MA120趋势过滤")

content = "\n".join(report)

print(content)

msg = MIMEText(
    content,
    "plain",
    "utf-8"
)

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

print("邮件发送成功")
