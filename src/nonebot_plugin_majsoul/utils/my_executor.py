import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from os import cpu_count

my_executor = ThreadPoolExecutor(cpu_count())


async def run_in_my_executor(func, *args, **kwargs):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(my_executor, partial(func, *args, **kwargs))
