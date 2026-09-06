# =============================================================================
# python_scripts/03_async_advanced.py  --  LEVEL: ADVANCED
# =============================================================================
# Purpose: async/await + asyncio — the core of FastAPI's concurrency model.
# This is THE topic that separates mid-level from senior backend interviews.
#
# KEY MENTAL MODEL (interview answer):
#   * `async def`  -> this function is a coroutine. Calling it returns a
#     coroutine OBJECT; it only runs when awaited/scheduled.
#   * `await`     -> "call this coroutine and BLOCK here until it finishes,
#                     but meanwhile let the event loop run OTHER tasks."
#   * The event loop  -> a single-threaded scheduler that juggles many coroutines.
#   * ASYNC I/O is for I/O-bound work (DB calls, HTTP requests, file reads).
#     THREADS are for CPU-bound work. They are NOT interchangeable.
#
# WHY FASTAPI IS FAST: sync endpoints run in a threadpool; async endpoints run
# on the event loop. Both free up the loop so many requests are handled
# concurrently without threads/processes per request.

import asyncio
import random


# --- Coroutine basics --------------------------------------------------------
async def greet(name: str) -> str:
    # `await asyncio.sleep` simulates slow I/O. It yields control to the loop,
    # so OTHER coroutines run during this sleep — that's the concurrency win.
    await asyncio.sleep(0.1)
    return f"Hello {name}"


async def main_greet():
    # Running three coroutines CONCURRENTLY via gather (~0.1s total, not 0.3s).
    results = await asyncio.gather(greet("a"), greet("b"), greet("c"))
    print(results)


# --- Real-world example: concurrent HTTP-like calls --------------------------
async def fetch_data(task_id: int) -> int:
    # Simulate a network/DB call: random latency.
    await asyncio.sleep(random.uniform(0.1, 0.3))
    return task_id * 10


async def run_many_fetches():
    # Create 20 coroutine objects, run them concurrently, collect results.
    tasks = [fetch_data(i) for i in range(20)]
    results = await asyncio.gather(*tasks)
    print("sum of concurrent fetches =", sum(results))


# --- Sequential vs concurrent: the punchline ---------------------------------
def sync_version(n: int):
    import time
    start = time.perf_counter()
    for i in range(n):
        time.sleep(0.2)                     # blocking — each waits its turn
    return time.perf_counter() - start


async def async_version(n: int):
    # all sleeps happen in parallel on the same single thread
    await asyncio.gather(*(asyncio.sleep(0.2) for _ in range(n)))


async def compare():
    import time
    s = time.perf_counter()
    sync_secs = sync_version(5)
    a = time.perf_counter()
    await async_version(5)
    async_secs = time.perf_counter() - a
    print(f"sync  = {sync_secs:.2f}s   async = {async_secs:.2f}s  (5 tasks)")
    # Output shows async ~5x faster though there's only ONE thread.
    # That's why FastAPI prefers `await` over blocking calls.


# --- TaskGroup (3.11+) vs gather (3.10 compatible) ---------------------------
# On 3.10 we use asyncio.gather / create_task. A note: `asyncio.TaskGroup`
# (cancellation-aware) only exists on 3.11+. We stay 3.10-compatible here.
async def fire_and_forget():
    coro = greet("background")
    task = asyncio.create_task(coro)   # schedule without awaiting right now
    await asyncio.sleep(0.2)           # let the loop run the task meanwhile
    print("created_task done:", task.done())


# --- Main entry --------------------------------------------------------------
async def main():
    await main_greet()
    await run_many_fetches()
    await compare()
    await fire_and_forget()


if __name__ == "__main__":
    # asyncio.run() creates a fresh event loop, runs main(), then closes it.
    asyncio.run(main())
    print("\nDone. Fun fact: your FastAPI async endpoints run exactly like this.")
