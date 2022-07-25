from datetime import datetime, timedelta, timezone

from apis.finance_data import *
from apis.trade import *
from config import STRATEGY_NAME
from run_strategy import AccountContext
from utils import abspath
from utils.logger_tools import get_general_logger
from pprint import pprint

# My import
from matplotlib import pyplot as plt
import pandas as pd
from pyecharts.charts import Kline
import numpy as np


logger = get_general_logger(STRATEGY_NAME, path=abspath("logs"))

def plot_kline(name,symbol,kline):
    df = pd.DataFrame(kline) # 将json转换为dataframe
    data = df[["open","close","high","low"]].values.tolist() # 取出开盘、收盘、最高、最低数据，并转换为list
    time = [t.split()[0] for t in df['datetime'].values.tolist()] # 取出时间，截取日期
    kline_plot = Kline() # 创建kline对象
    kline_plot.add_xaxis(time) # 添加横坐标
    kline_plot.add_yaxis(f'{name}({symbol}) 日 K 线图',data) # 添加纵坐标
    kline_plot.render() # 保存html

def main(context: AccountContext):
    # 股票代码
    symbol = "SH.600030"
    info = get_stock_info(symbol)
    # print(info)
    name = info['名称']

    # 获取近5日K线数据
    kline_end = datetime.now(timezone(timedelta(hours=8)))
    kline_start = kline_end - timedelta(days=100) + timedelta(seconds=1)
    kline = get_kline(
        symbol,
        kline_start.strftime("%Y-%m-%d %H:%M:%S"),
        kline_end.strftime("%Y-%m-%d %H:%M:%S"),
        "1d",  # 天级
    )
    # pprint(kline)
    if len(kline) == 0:
        logger.warning(f"未查询到K线信息，请检查股票代码({symbol})或时间是否正确。若无误，请联系管理员。")
        return

    获取当前持仓
    pos_amount = sum(
        pos["amount"]
        for pos in filter(
            lambda pos: symbol == pos["symbol"], context.positions["avaliable"]
        )
    )
    logger.info(f"当前持仓：{pos_amount}")

    # 计算近5日均值
    ma_close = sum([info["close"] / len(kline) for info in kline])
    latest_close = kline[-1]["close"]
    diff_pct = round((latest_close - ma_close) * 100 / ma_close, 2)
    logger.info(f"平均: {ma_close}, 最新: {latest_close}, 差值: {diff_pct}%")

    # close_data = [info["close"] for info in kline]
    # plt.plot(close_data)
    # plt.savefig("kline.png")
    
    plot_kline(name,symbol,kline)

    # 样例策略
    max_pos_amount = 300  # 最大持仓量

    # 买入
    buy_amount = 100  # 买入量（须为100的倍数）
    if (
        context.cash_avaliable > latest_close * buy_amount  # 现金充足
        and pos_amount + buy_amount <= max_pos_amount  # 交易后不超过最大持仓量
        and latest_close >= ma_close * 1.01  # 现价超过均价至少1%
    ):
        make_order(symbol, "market", "buy", buy_amount)
        logger.info(f"买入策略已执行")
        return

    # 卖出
    if pos_amount > max_pos_amount + 100:  # 实际持仓量大于最大持仓量100股
        sell_amount = (pos_amount - max_pos_amount) // 100 * 100  # 卖出超过阈值的持仓量（须为100的倍数）
        make_order(symbol, "market", "sell", sell_amount)
        logger.info(f"卖出策略已执行")
        return

