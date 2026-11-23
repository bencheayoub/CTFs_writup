# Picker I

| | |
|---|---|
| **Category** | Reverse Engineering |
| **Difficulty** | Easy |
| **Author** | LT 'syreal' Jones |
| **Files** | `picker-I.py` |
| **Flag** | `academy{4_d14m0nd_1n_7h3_r0ugh_c55fbef5}` |

## Challenge

> This service can provide you with a random number, but can it do anything else?

## Analysis

The program is a loop that reads input and passes it to `eval`, appending `()`:

```python
while(True):
  try:
    print('Try entering "getRandomNumber" without the double quotes...')
    user_input = input('==> ')
    eval(user_input + '()')
  except Exception as e:
    print(e)
    break
```

So whatever name we type is looked up and **called**. The hint says `getRandomNumber`, but any function defined in the file can be called. Besides the decoys (`esoteric1`, `esoteric2`, `exit`), there is:

```python
def win():
  flag = open('flag.txt', 'r').read()
  flag = flag.strip()
  str_flag = ''
  for c in flag:
    str_flag += str(hex(ord(c))) + ' '
  print(str_flag)
```

`win` is never referenced by the menu, but nothing stops us from calling it.

## Exploration notes

Things tried before reading the source properly:

| Input | Result | Why |
|---|---|---|
| `"getRandomNumber"` | `'str' object is not callable` | becomes `"getRandomNumber"()` |
| `print(flag)` | `name 'flag' is not defined` | `flag` is local to `win()` |
| `getFlag`, `main` | `name ... is not defined` | guessed names that don't exist |
| `122` | `'int' object is not callable` | `122()` |

## Exploit

```
==> win
0x61 0x63 0x61 0x64 0x65 0x6d 0x79 0x7b 0x34 0x5f 0x64 0x31 0x34 0x6d 0x30 0x6e 0x64 0x5f 0x31 0x6e 0x5f 0x37 0x68 0x33 0x5f 0x72 0x30 0x75 0x67 0x68 0x5f 0x63 0x35 0x35 0x66 0x62 0x65 0x66 0x35 0x7d
```

The flag is printed as space-separated hex bytes. Decode:

```python
h = "0x61 0x63 0x61 ... 0x7d"
print(''.join(chr(int(x, 16)) for x in h.split()))
# academy{4_d14m0nd_1n_7h3_r0ugh_c55fbef5}
```

## Takeaways

- `eval()` on user input gives arbitrary code execution; even with `+ '()'` appended, any callable in scope is reachable.
- Read the whole source: unused functions like `win` are usually the target.
