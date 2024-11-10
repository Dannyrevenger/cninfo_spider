import asyncio
from collections import defaultdict
from playwright.async_api import async_playwright
from datetime import datetime
from utils.setup_log import logger
from utils.docs_operate import *
from spider.decorator import *


@record_error_then_continue
async def open_url(page, code, url) -> None:
    logger.info(f'[-]{code}尝试打开cninfo...')
    await page.goto("http://www.cninfo.com.cn/new/index")
    # Wait for the await page to fully load
    await page.wait_for_url("http://www.cninfo.com.cn/new/index")
    logger.success(f'[+]{code}成功打开cninfo！')


@record_error_then_continue
async def search_announce(page, code, start_date, end_date):
    logger.info('[-]选择日期和输入代码...')
    await page.get_by_placeholder("代码/简称/拼音", exact=True).click()
    await page.get_by_placeholder("代码/简称/拼音", exact=True).fill(code)
    await page.get_by_title(code).click(timeout=5000)
    # await page.get_by_text(code).click(timeout=5000)
    await page.get_by_placeholder("开始日期").click()
    await page.get_by_placeholder("开始日期").fill(start_date)
    await page.get_by_placeholder("开始日期").press("Enter")
    await page.get_by_placeholder("结束日期").click()
    await page.get_by_placeholder("结束日期").fill(end_date)
    await page.get_by_placeholder("结束日期").press("Enter")
    await page.get_by_role("button", name="查询").click()
    logger.info('[-]跳转查询页面...')


async def scratch_cninfo(contents, start_date, end_date):
    failed_codes = []
    hyperlinks = defaultdict(dict)
    async with async_playwright() as p:
        # Launch the browser
        logger.info('[-]创建浏览器实例...')
        browser = await p.chromium.launch(executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", headless=True)

        # Create a new browser context
        context = await browser.new_context()

        # Open a new await page
        page = await context.new_page()
        # Initialize hyperlinks as a defaultdict of dictionaries
        for company_name, code in contents.items():
            # hyperlinks[company_name] = {}
            error_handler = await open_url(page, code, "http://www.cninfo.com.cn/new/index")
            if error_handler:
                failed_codes.append(error_handler[1])
                continue
            error_handler = await search_announce(page, code, start_date, end_date)
            if error_handler:
                failed_codes.append(error_handler[1])
                continue
            try:
                # Wait for the page to be idle after network activity
                await page.wait_for_load_state('networkidle')
                # Get a locator for all elements that match the 'span.ahover.ell a' selector
                rows = page.locator("tbody tr.el-table__row")
                # Count how many elements match this locator
                count = await rows.count()
                # Loop through all matching elements and get the 'href' attribute for each
                if count > 0:
                    for i in range(count):
                        anchor = rows.nth(i).locator("td.el-table_1_column_3 .cell a")
                        title = await anchor.get_attribute("title")
                        href = await anchor.get_attribute("href")
                        # Extract the date within the fourth column
                        date_text = await rows.nth(i).locator("td.el-table_1_column_4 .cell .date").text_content()
                        logger.success(f'[+]在cninfo {code}查询到{title}!')
                        if company_name not in hyperlinks:
                            hyperlinks[company_name] = {}
                        if title not in hyperlinks[company_name]:
                            hyperlinks[company_name][title] = {}
                        hyperlinks[company_name][title][date_text] = 'http://www.cninfo.com.cn' + href
                else:
                    logger.info(f'[+]{code}暂无新公告!')
            except Exception as e:
                logger.error(f'{code}在返回cninfo结果时没有成功执行!')
                logger.error(e)
                failed_codes.append(code)
                continue

            await page.pause()
        await page.close()
        await browser.close()

    return hyperlinks, failed_codes



