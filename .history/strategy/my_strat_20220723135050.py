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
    symbol = "SZ.000100"

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

    logger.info("Hello world!")