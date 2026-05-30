# 🔐 CTF Writeup — `crackme` (ARM64 Reverse Engineering)

> **Category:** Reverse Engineering  
> **Architecture:** Mach-O 64-bit · arm64  
> **Language:** Swift (compiled)  
> **Difficulty:** Beginner–Intermediate  
> **Flag:** `FLAG{4rm64_r3v_is_fun}`

---

## 📜 Challenge Description

> _A retired embedded systems engineer encrypted his life's work before vanishing. All that remains is a small utility he wrote. It asks for something. Can you find it?_

---

## 🛠️ Tools Used

| Tool                     | Purpose                                  |
| ------------------------ | ---------------------------------------- |
| `file`                   | Identify binary type                     |
| `xxd`                    | Hex dump the binary                      |
| `dd`                     | Extract raw bytes from a specific offset |
| `radare2` / disassembler | Static analysis / disassembly            |
| `Python 3`               | Write the flag solver                    |

---

## 🔍 Step 1 — Reconnaissance

First, identify what we're dealing with:

```bash
file crackme
# crackme: Mach-O 64-bit arm64 executable, flags:<NOUNDEFS|DYLDLINK|TWOLEVEL|PIE>
```

Key observations:

- **Mach-O** → macOS binary
- **arm64** → Apple Silicon architecture
- **PIE** → Position Independent Executable (ASLR-enabled)
- The binary is compiled from **Swift** (visible from imported symbols like `swift_allocObject`, `swift_bridgeObjectRelease`, `readLine`)

---

## 🔬 Step 2 — Static Analysis

Disassembling the binary reveals a clean `main` function. Here's the high-level flow:

```
main()
 ├── Print "Enter flag: "
 ├── readLine() → read user input
 ├── call _validate(input_ptr, input_length)
 │    ├── if result == 1 → print "Correct!"
 │    └── if result == 0 → print "Wrong."
 └── exit
```

The core logic lives entirely inside `_validate`.

---

## 🔐 Step 3 — Reversing `_validate`

The `_validate` function starts at `0x100000c70`. Let's walk through it instruction by instruction.

### 3.1 — Length Check

```asm
0x100000c70   cmp  x1, 0x16
0x100000c74   b.ne 0x100000d10   ; jump to "return 0" if length != 22
```

The input **must be exactly 22 characters long**. Any other length → immediate fail.

```asm
0x100000d10   mov  w0, 0
0x100000d14   ret
```

### 3.2 — The Per-Character Transform

For each character at index `i`, the binary applies this sequence:

```asm
ldrb  w10, [x8]        ; load input[i]
and   w0, w10, 0xff    ; mask to byte
mov   w3, 0x5a         ; constant = 'Z' = 0x5A
eor   w0, w0, w3       ; XOR with 0x5A
ror   w0, w0, 3        ; rotate right by 3 bits (8-bit)
and   w0, w0, 0xff     ; mask to byte
add   w0, w0, w9       ; add current index i
and   w10, w0, 0xff    ; mask to byte  ← this is the result
```

In Python:

```python
def transform(char, index):
    v = (ord(char) ^ 0x5A) & 0xFF
    v = ((v >> 3) | (v << 5)) & 0xFF   # ROR8 by 3
    v = (v + index) & 0xFF
    return v
```

### 3.3 — Comparison Against the Secret Table

After transforming each character, the result is compared against a hardcoded byte table stored in the `__DATA.__ckdata` section:

```asm
adrp  x9, section.__DATA.__ckdata   ; load table base address
ldrb  w13, [x9, x10]                ; load table[i]
cmp   w13, w12, uxtb                ; compare with transform(input[i], i)
b.eq  loop_continue                 ; if equal, keep going
; else: fail
```

The function returns `1` (correct) only if **all 22 characters** pass this check.

---

## 📦 Step 4 — Extracting the Secret Table

The `__ckdata` section is described in the Mach-O section headers. We find it by dumping the binary header:

```bash
xxd crackme | grep -A2 "00008000:"
```

Output:

```
00008000: 0000 0000 0000 0000 83c3 65a6 28d2 0bed  ..........e.(...
00008010: 95d6 aa10 3992 ae75 35b1 99f8 9af9 0000  ....9..u5.......
```

The table starts at file offset `0x8008` (8 bytes into the `__DATA` segment, right after the 8-byte `__data` section). We extract exactly 22 bytes:

```bash
dd if=crackme bs=1 skip=$((0x8008)) count=22 2>/dev/null | xxd
```

Output:

```
00000000: 83c3 65a6 28d2 0bed 95d6 aa10 3992 ae75  ..e.(.......9..u
00000010: 35b1 99f8 9af9                           5.....
```

The 22 table bytes are:

```
83 c3 65 a6 28 d2 0b ed 95 d6 aa 10 39 92 ae 75 35 b1 99 f8 9a f9
```

---

## 🧮 Step 5 — Inverting the Transform

We have the forward transform:

```
table[i] = ROR8(input[i] XOR 0x5A, 3) + i   (mod 256)
```

To recover `input[i]`, we invert it:

```
step1 = (table[i] - i) & 0xFF          # undo the addition
step2 = ROL8(step1, 3)                 # undo the rotation (ROL = inverse of ROR)
input[i] = step2 XOR 0x5A             # undo the XOR
```

### Verification — First Character

```
table[0] = 0x83
step1 = (0x83 - 0) & 0xFF = 0x83
step2 = ROL8(0x83, 3) = 0001 1100 = 0x1C   (rotate left: 1000 0011 → 0001 1100 0 wait...)

ROL8(0x83, 3):
  0x83 = 1000 0011
  shift left 3:  0001 1000  (upper 3 bits wrap around)
  wrap bits:     000  →  added at right? No — let's be precise:
  ROL8(v, n) = ((v << n) | (v >> (8-n))) & 0xFF
  = ((0x83 << 3) | (0x83 >> 5)) & 0xFF
  = (0x418 | 0x04) & 0xFF
  = 0x1C

input[0] = 0x1C XOR 0x5A = 0x46 = 'F'  ✓
```

The flag starts with `'F'` — consistent with the `FLAG{...}` format.

---

## 💻 Step 6 — The Solver Script

```python
table = [
    0x83, 0xc3, 0x65, 0xa6, 0x28, 0xd2, 0x0b, 0xed,
    0x95, 0xd6, 0xaa, 0x10, 0x39, 0x92, 0xae, 0x75,
    0x35, 0xb1, 0x99, 0xf8, 0x9a, 0xf9
]

def rol8(v, n):
    v &= 0xFF
    return ((v << n) | (v >> (8 - n))) & 0xFF

flag = ""
for i, t in enumerate(table):
    step1 = (t - i) & 0xFF       # undo: add index
    step2 = rol8(step1, 3)       # undo: ROR8 by 3  →  ROL8 by 3
    c     = step2 ^ 0x5A         # undo: XOR 0x5A
    flag += chr(c)

print(f"Flag: {flag}")
```

**Output:**

```
Flag: FLAG{4rm64_r3v_is_fun}
```

---

## 🗺️ Summary

```
Input char[i]
      │
      ▼
  XOR 0x5A
      │
      ▼
  ROR8 by 3
      │
      ▼
  + index i  (mod 256)
      │
      ▼
  == table[i]  ?  →  Correct! / Wrong.
```

|Step|Transform|Inverse|
|---|---|---|
|1|`c XOR 0x5A`|`result XOR 0x5A`|
|2|`ROR8(v, 3)`|`ROL8(v, 3)`|
|3|`(v + i) mod 256`|`(v - i) mod 256`|

---

## 🏁 Flag

```
FLAG{4rm64_r3v_is_fun}
```

---

## 📚 Lessons Learned

- **Mach-O binaries** follow a segment/section structure. The `__DATA.__ckdata` section was a non-standard custom section used to hide the validation table — worth checking all sections, not just `__data`.
- **Swift binaries** are fully reversible with static analysis despite the name-mangled symbols. The core logic compiles down to clean ARM64 instructions.
- **ROR/ROL** are common obfuscation primitives in crackmes. Always check for rotation instructions (`ror`, `rol`) combined with XOR — they're easy to invert once identified.
- **Index-dependent transforms** (`+ i`) make each character's encoding unique, preventing frequency analysis, but they're still trivially invertible when you control the index.
