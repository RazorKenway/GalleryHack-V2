#path /data/data/com.termux/files/usr/lib/python3.11/site-packages/tenacity

try:
    import asyncio
except ImportError:
    asyncio = None

import sys

from tenacity import BaseRetrying
from tenacity import DoAttempt
from tenacity import DoSleep
from tenacity import RetryCallState

if asyncio:
    class AsyncRetrying(BaseRetrying):

        def __init__(self,
                     sleep=asyncio.sleep,
                     **kwargs):
            super(AsyncRetrying, self).__init__(**kwargs)
            self.sleep = sleep

        async def call(self, fn, *args, **kwargs):
            self.begin(fn)

            retry_state = RetryCallState(
                retry_object=self, fn=fn, args=args, kwargs=kwargs)
            while True:
                do = self.iter(retry_state=retry_state)
                if isinstance(do, DoAttempt):
                    try:
                        result = await fn(*args, **kwargs)  # Use 'await' instead of 'yield from'
                    except BaseException:
                        retry_state.set_exception(sys.exc_info())
                    else:
                        retry_state.set_result(result)
                elif isinstance(do, DoSleep):
                    retry_state.prepare_for_next_attempt()
                    await self.sleep(do)  # Use 'await' instead of 'yield from'
                else:
                    return do
