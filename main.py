import asyncio

from spider.cninfo import *
from spider.sina import *
from utils.logs_operate import *


async def start_main(codes, start_date, end_date, keywords):
    task1 = asyncio.create_task(scratch_cninfo(codes, start_date, end_date))
    task2 = asyncio.create_task(scratch_sina(codes, start_date, keywords))
    c_links, c_f_codes = await task1
    s_links, s_f_codes = await task2
    return c_links, c_f_codes, s_links, s_f_codes
    # return c_links, c_f_codes


def convert_failed_codes_to_contents(failed_codes, company_codes):
    _failed_contents = defaultdict(dict)
    for failed_code in failed_codes:
        for key, value in company_codes.items():
            if value == failed_code:
                _failed_contents[key] = value  # 将符合条件的键值对添加到新字典中
    return _failed_contents











