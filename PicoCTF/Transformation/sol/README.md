# Transformation

| | |
|---|---|
| **Category** | Reverse Engineering |
| **Difficulty** | Easy |
| **Author** | madStacks (picoCTF 2021) |
| **Files** | `enc`, `decrypt.py` |
| **Flag** | `academy{16_bits_inst34d_of_8_790ba37e}` |

## Challenge

> I wonder what this really is... `enc`

The challenge gives the encrypted output and the line that produced it:

```python
''.join([chr((ord(flag[i]) << 8) + ord(flag[i + 1])) for i in range(0, len(flag), 2)])
```

## Analysis

The code walks through the flag **two characters at a time** (`range(0, len(flag), 2)`) and packs each pair into **one** 16-bit character:

```
code point = (flag[i] << 8) + flag[i+1]
              high byte        low byte
```

For example `"ac"` = `0x61 0x63` becomes code point `0x6163`, which is the CJK character `慣`. That's why the ciphertext looks like random Chinese text: each character holds two ASCII bytes.

```
enc = "慣慤敭祻ㄶ形楴獟楮獴㌴摟潦弸強㤰扡㌷敽"
```

This is an encoding, not encryption. There's no key and nothing lost, so it is trivially reversible.

## Solution

Split each character back into its high and low bytes:

```python
enc = "慣慤敭祻ㄶ形楴獟楮獴㌴摟潦弸強㤰扡㌷敽"

def decrypt(enc):
    dec = ''
    for c in enc:
        dec += chr(ord(c) >> 8)      # high byte -> first char
        dec += chr(ord(c) & 0xFF)    # low byte  -> second char
    return dec

print(f'Decrypted flag: {decrypt(enc)}')
```

Output:

```
Decrypted flag: academy{16_bits_inst34d_of_8_790ba37e}
```

The flag text itself gives the hint: 16 bits instead of 8.

## Takeaways

- Strings of CJK characters that look random are often just two bytes packed per code point; check `ord()` values and the high byte (`0x61`..`0x7e` is printable ASCII).
- When given the encoder, write the inverse operation step by step: `<<` and `+` become `>>` and `& 0xFF`.
