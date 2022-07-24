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
    r = get_concept_board_list()
    print(r)
    logger.info("Hello world!")