import asyncio
import re
from collections import defaultdict
from playwright.async_api import async_playwright
from datetime import datetime
from utils.setup_log import logger
from utils.docs_operate import *
from spider.which_market import *
from spider.decorator import *
import platform


@record_error_then_continue
async def open_url(page, code, web):
    logger.info(f'[-]{code}尝试打开sina...')
    await page.goto(web)  # Navigate to the Sina website
    # Wait for the await page to fully load
    await page.wait_for_url(web)  # Wait until network activity is idle (all resources loaded)
    logger.success(f'[+]{code}成功打开sina！')


async def scratch_sina(contents, date, keywords):
    # Initialize hyperlinks as a defaultdict of dictionaries
    failed_code = []
    hyperlinks = defaultdict(dict)
    async with async_playwright() as p:
        # Launch the browser
        logger.info('[-]创建浏览器实例...')
        system = platform.system()
        if system == "Darwin":
            browser = await p.chromium.launch(executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", headless=True)
        elif system == "Windows":
            browser = await p.chromium.launch(headless=True)
        # Create a new browser context
        context = await browser.new_context()

        # Open a new await page
        page = await context.new_page()
        for company_name, company_code in contents.items():
            code = get_stock_market(company_code)
            web = f"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/{code}.phtml"
            error_handler = await open_url(page, code, web)
            if error_handler:
                failed_code = error_handler[1]
                continue
            try:
                logger.info('[-]跳转查询页面...')
                elements = await page.locator('.datelist ul').all_inner_texts()
                elements = ''.join(elements)
                news = elements.split('\n')
                for item in news:
                    date_part = re.findall(r'\d{4}-\d{2}-\d{2}', item)
                    date_part = ''.join(date_part)
                    if date_part == date:
                        title = re.sub(r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}\s+', '', item).replace("\xa0", "")
                        if "融资" not in title and "融券" not in title:
                            if len(keywords) > 0:
                                keywords_list = keywords.split('，')
                                key_count = 0
                                for keyword in keywords_list:
                                    if keyword in title:
                                        key_count += 1
                                if key_count == 0:
                                    try:
                                        link = page.get_by_role("link", name=title)
                                        url = await link.get_attribute('href')
                                    except:
                                        link = page.get_by_role("link", name=title).nth(0)
                                        url = await link.get_attribute('href')
                                    logger.success(f'[+]在sina，{code}查询到"{title}"!')
                                    hyperlinks[company_name][title] = url

                            else:
                                try:
                                    link = page.get_by_role("link", name=title)
                                    url = await link.get_attribute('href')
                                except:
                                    link = page.get_by_role("link", name=title).nth(0)
                                    url = await link.get_attribute('href')
                                logger.success(f'[+]在sina，{code}查询到"{title}"!')
                                hyperlinks[company_name][title] = url

            except Exception as e:
                logger.error(f'{code}在返回sina结果时没有成功执行!')
                logger.error(e)
                failed_code.append(code)
                continue
            await page.pause()

        await page.close()
        await browser.close()
    return hyperlinks, failed_code



