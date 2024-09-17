import asyncio


def run_async(func, *args):
    # loop = asyncio.get_event_loop()
    return asyncio.run(func(*args))
