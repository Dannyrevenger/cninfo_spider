from utils.setup_log import logger


def record_error_then_continue(func):
    async def wrapper(*args, **kwargs):
        try:
            await func(*args, **kwargs)
        except Exception as e:
            logger.error(f'在 {func.__name__} 没有成功执行!')
            logger.error(f'传递的参数: args = {args}, kwargs = {kwargs}')
            logger.error(e)
            return args
    return wrapper