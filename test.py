import asyncio
loop = asyncio.get_event_loop()
delay = 100.0

async def my_func():
    # твоя логика с отправкой сообщений тут
    
    when_to_call = loop.time() + delay  # delay -- промежуток времени в секундах.
    loop.call_at(when_to_call, my_callback)
    await print("Im asynchronus")

def my_callback():
    asyncio.ensure_future(my_func())

my_callback()