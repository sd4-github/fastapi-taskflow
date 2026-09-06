# =============================================================================
# python_scripts/02_intermediate.py  --  LEVEL: INTERMEDIATE
# =============================================================================
# Purpose: the "language features" interviews probe for a backend role.
# Topics: dataclasses, *args/**kwargs, decorators, generators, context managers,
#         exceptions, typing (Optional/Union/List), lambda, map/filter, functools.
# Run with:  .venv/bin/python python_scripts/02_intermediate.py

from dataclasses import dataclass, field
from functools import lru_cache, reduce
from typing import Optional, Union
import time


# --- 1) dataclasses ---------------------------------------------------------
# A dataclass auto-generates __init__, __repr__, __eq__ for you.
# Perfect for small structured values (like a lightweight Pydantic model).
@dataclass
class Task:
    title: str
    done: bool = False
    tags: list[str] = field(default_factory=list)  # mutable default needs factory!

t = Task("Fix bug", tags=["urgent"])
print(t, t.title, t.done)          # __repr__ gives readable output

# field(default_factory=list): NEVER write `tags: list = []` — a mutable default
# (empty list) is SHARED across all instances of the class -> classic Python gotcha.


# --- 2) *args / **kwargs -----------------------------------------------------
# *args  -> collects extra POSITIONAL args into a tuple
# **kwargs-> collects extra KEYWORD args into a dict
def log(level: str, *args, **kwargs) -> None:
    print(f"[{level}]", args, kwargs)

log("INFO", "user logged in", user_id=42)


# --- 3) Decorators -----------------------------------------------------------
# A decorator wraps a function to add behavior without changing its body.
# The inner function *closes over* `func` (closure — see below).
def log_calls(func):
    def wrapper(*args, **kwargs):
        print(f"CALLING {func.__name__} with {args} {kwargs}")
        result = func(*args, **kwargs)
        print(f"RETURNED {result!r}")
        return result
    return wrapper

@log_calls                 # sugar for: get_user = log_calls(get_user)
def get_user(uid: int) -> str:
    return f"user-{uid}"

get_user(7)


# --- 4) Closure -------------------------------------------------------------
# A closure = inner function that remembers variables from its outer scope
# even after the outer function returns. Decorators rely on this.
def make_multiplier(factor: int):
    def multiply(x: int) -> int:
        return x * factor       # `factor` is captured (remembered)
    return multiply

double = make_multiplier(2)
print(double(10))               # 20


# --- 5) Generators -----------------------------------------------------------
# A generator yields values lazily — one at a time, on demand. It does NOT
# build a big list in memory (great for huge data / infinite streams).
# FastAPI's `yield` dependency uses exactly this pattern.
def countdown(n: int):
    while n > 0:
        yield n                 # pause here, hand `n` to the caller
        n -= 1

for x in countdown(3):
    print("tick", x)

# Generator expression (lazy) vs list comprehension (eager)
lazy_sum = sum(x * x for x in range(100))     # <-- generator expr (memory-lean)
print(lazy_sum)


# --- 6) Context managers (with ...) ------------------------------------------
# `with` guarantees setup/cleanup even if an error happens (e.g. closing a DB
# session, releasing a lock). FastAPI get_db uses try/finally — same idea.
class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"elapsed: {time.perf_counter() - self.start:.5f}s")
        return False            # False => don't suppress exceptions

with Timer():
    time.sleep(0.05)


# --- 7) Exceptions -----------------------------------------------------------
# Raise specific exceptions; catch narrowly (not bare `except:`).
def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("cannot divide by zero")
    return a / b

try:
    divide(1, 0)
except ValueError as e:
    print("caught:", e)
finally:
    print("always runs (cleanup)")


# --- 8) Type hints: Optional / Union / List ----------------------------------
# String-versions are fine too; modern Python allows `X | None`.
def fetch(key: str) -> Optional[int]:   # may return None
    return None

def combine(a: Union[int, str], b: int | str) -> str:  # Union == `|`
    return f"{a}{b}"


# --- 9) functools: lru_cache -------------------------------------------------
# Memoize: cache function results so repeated calls with the same args are O(1).
# FastAPI config uses lru_cache for a singleton Settings().
@lru_cache(maxsize=128)
def fib(n: int) -> int:
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

print("fib(30) =", fib(30))   # instant thanks to cache

# reduce = fold a sequence into one value
total = reduce(lambda acc, x: acc + x, [1, 2, 3, 4])
print("reduce sum =", total)

# map/filter are lazy iterators, usually pre-empted by comprehensions
names = list(map(str.upper, ["a", "b"]))
print(names)
