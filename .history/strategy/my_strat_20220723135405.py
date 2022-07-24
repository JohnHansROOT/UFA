from datetime import datetime, timedelta, timezone

from apis.finance_data import *
from apis.trade import *
from config import STRATEGY_NAME
from run_strategy import AccountContext
from utils import abspath
from utils.logger_tools import get_general_logger
from pprint import pprint

logger = get_general_logger(STRATEGY_NAME, path=abspath("logs"))


def main(context: AccountContext):
    # 股票代码
    symbol = "SH.600030"

    # 获取近5日K线数据
    kline_end = datetime.now(timezone(timedelta(hours=8)))
    kline_start = kline_end - timedelta(days=6) + timedelta(seconds=1)
    kline = get_kline(
        symbol,
        kline_start.strftime("%Y-%m-%d %H:%M:%S"),
        kline_end.strftime("%Y-%m-%d %H:%M:%S"),
        "1d",  # 天级
    )
    pprint(kline)
    if len(kline) == 0:
        logger.warning(f"未查询到K线信息，请检查股票代码({symbol})或时间是否正确。若无误，请联系管理员。")
        return

    # 获取当前持仓
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

    # 样例策略
    max_pos_amount = 300  # 最大持仓量

    logger.info("Hello world!")