# =============================================================================
# python_scripts/01_basics.py  --  LEVEL: BASIC
# =============================================================================
# Purpose: warm up core Python before using the framework. Read top-to-bottom.
# Run with:  .venv/bin/python python_scripts/01_basics.py
#
# Topics: variables, built-in types, f-strings, control flow, functions,
#         collections (list/dict/set/tuple), list comprehensions, unpacking.
# These are THE fundamentals every interview assumes you know cold.

# --- Data types -----------------------------------------------------------
name: str = "TaskFlow"              # type hint (optional but documents intent)
count: int = 3
price: float = 19.99
is_active: bool = True
tags: list[str] = ["todo", "urgent"]  # list of strings (new-style generics)
meta: dict[str, int] = {"tasks": 5}   # dict str->int
unique: set[int] = {1, 2, 3}          # set = unique, unordered
point: tuple[int, int] = (1, 2)       # tuple = fixed-size

# f-strings: the modern way to build strings (interpolation + formatting)
print(f"Hello {name} — {count} items at ${price:.2f}")

# --- Control flow ----------------------------------------------------------
if price > 10 and is_active:
    pass
elif price > 5:
    pass
else:
    pass

for i in range(3):
    print(f"loop {i}")

# while with break/continue
n = 0
while n < 5:
    n += 1
    if n == 2:
        continue     # skip rest of iteration
    if n == 4:
        break        # stop the loop entirely

# --- Functions --------------------------------------------------------------
def add(a: int, b: int) -> int:
    """Docstring: explains what the function does. Return type hint: -> int."""
    return a + b

def greet(name: str = "world", *, loud: bool = False) -> str:
    """Default arg + keyword-only arg (* after `*` must be passed by name)."""
    return f"HELLO {name}" if loud else f"Hello {name}"

print(add(1, 2), greet(loud=True))

def sum_all(*args: int) -> int:
    """*args collects any number of positional args into a tuple."""
    return sum(args)

# --- Collections & comprehensions ------------------------------------------
# list comprehension = concise loop->list
squares = [x * x for x in range(5)]          # [0, 1, 4, 9, 16]
evens = [x for x in range(10) if x % 2 == 0] # with filter
pairs = {k: v for k, v in [("a", 1), ("b", 2)]}  # dict comprehension

# unpacking / destructuring
a, b = 1, 2
first, *rest, last = [1, 2, 3, 4, 5]        # first=1, rest=[2,3,4], last=5
head, *_ = [10, 20, 30]                     # head=10, ignore rest

# enumerate = index + value together (better than range(len()))
for idx, val in enumerate(["x", "y"]):
    print(idx, val)

# zip = walk multiple sequences together
for num, tag in zip([1, 2], ["one", "two"]):
    print(num, tag)

# dict.get with default avoids KeyError crashes
d = {"a": 1}
print(d.get("missing", 0))                  # 0 instead of crashing

# set/dict membership is O(1) — much faster than list "in" for big data
print("a" in d)                              # fast membership check

if __name__ == "__main__":
    # This guard means the code only runs when executed directly,
    # not when imported elsewhere. Standard practice.
    print("01_basics.py ran; init steps above skipped imports cleanly")
