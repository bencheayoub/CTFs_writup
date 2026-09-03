# IronVest — Reverse Engineering Write-up

## Challenge Overview

**Challenge:** `IronVest.exe`
**Category:** Reverse Engineering
**Architecture:** Windows x64 PE
**Tool:** Ghidra

The challenge presents a program that asks for a number between `0` and `255`. The goal is to determine the correct input and recover the flag.

The initial message hints at defensive mechanisms:

> "I believe we've built a strong defensive design—no one should be able to jump to the hidden places."

This suggests that the binary contains anti-debugging or anti-analysis logic.

---

## 1. Initial Analysis

First, we inspect the executable with Ghidra.

The entry point initially looks like:

```c
void entry(void)
{
    __security_init_cookie();
    FUN_140001b24();
    return;
}
```

`entry()` itself does not contain the challenge logic. It simply initializes the security cookie and calls the Microsoft C runtime startup routine.

---

## 2. Following the Startup Code

Inside `FUN_140001b24()`, most of the code is standard CRT initialization.

The important call is:

```c
uVar5 = FUN_1400014b0(uVar9, uVar3, uVar5, in_R9);
```

Therefore, we follow:

```text
entry
  ↓
FUN_140001b24
  ↓
FUN_1400014b0
```

`FUN_1400014b0()` contains the actual challenge logic.

---

## 3. Finding the Input

Inside `FUN_1400014b0()`, we find:

```c
FUN_140001020("Enter a number (0-255): ", ...);
```

The input is stored in:

```c
local_128[0]
```

The program verifies that the value is less than `0x100`:

```c
if (local_128[0] < 0x100) {
    ...
}
```

So the accepted range is:

```text
0–255
```

---

## 4. Anti-Debugging Check

Before checking the answer, the program calls:

```c
uVar10 = FUN_1400010e0();
```

There are multiple calls to this function.

If the check fails, execution eventually reaches:

```c
FUN_140001020("\nAccess denied.\n", ...);
```

The binary also imports Windows APIs associated with process/debugger inspection, including:

```text
IsDebuggerPresent
CheckRemoteDebuggerPresent
GetThreadContext
CreateToolhelp32Snapshot
Process32FirstW
Process32NextW
```

This confirms that the challenge contains anti-analysis/anti-debugging mechanisms.

However, the mathematical validation can be analyzed statically without bypassing these checks.

---

## 5. Finding the Validation Formula

The critical code is:

```c
uVar12 = local_128[0];

uVar12 = (uVar12 * 0xd + 7 ^ 0x42) & 0xff;

if (((byte)((byte)(uVar12 >> 4) |
            (byte)(uVar12 << 4)) == 0x37) &&
    (DAT_140005664 == 0)) {
```

The important expression is:

```c
(input * 0xD + 7) ^ 0x42
```

followed by:

```c
& 0xFF
```

Then the two nibbles of the resulting byte are swapped.

The final value must be:

```text
0x37
```

---

## 6. Reverse the Nibble Swap

The operation:

```c
(byte)(uVar12 >> 4) | (byte)(uVar12 << 4)
```

swaps the high and low nibbles.

We need the result to be:

```text
0x37
```

Therefore, before the swap it must be:

```text
0x73
```

Because:

```text
0x73
 ↓ swap nibbles
0x37
```

So we need:

```text
((input * 0xD + 7) ^ 0x42) & 0xFF = 0x73
```

---

## 7. Reverse the XOR

We can undo the XOR by XORing both sides with `0x42`:

```text
input * 0xD + 7 = 0x73 ^ 0x42
```

Calculate:

```text
0x73 ^ 0x42 = 0x31
```

Therefore:

```text
input * 0xD + 7 = 0x31
```

or in decimal:

```text
13 × input + 7 = 49
```

Because the calculation is masked with `0xFF`, we actually solve it modulo `256`:

```text
13 × input + 7 ≡ 49 (mod 256)
```

Thus:

```text
13 × input ≡ 42 (mod 256)
```

---

## 8. Solve the Modular Equation

We need the modular inverse of `13` modulo `256`.

The inverse is:

```text
13⁻¹ ≡ 197 (mod 256)
```

Therefore:

```text
input ≡ 42 × 197 (mod 256)
```

Calculate:

```text
42 × 197 = 8274
```

and:

```text
8274 mod 256 = 82
```

Therefore:

```text
input = 82
```

---

## 9. Verify the Answer

Let's verify `82`.

Convert to hexadecimal:

```text
82 = 0x52
```

Calculate:

```text
0x52 × 0x0D + 7
```

In decimal:

```text
82 × 13 + 7
= 1066 + 7
= 1073
```

Apply the `0xFF` mask:

```text
1073 & 0xFF = 49
```

which is:

```text
0x31
```

Now XOR with `0x42`:

```text
0x31 ^ 0x42 = 0x73
```

Swap the nibbles:

```text
0x73 → 0x37
```

The comparison succeeds:

```c
== 0x37
```

Therefore, the correct input is:

```text
82
```

---

## 10. Finding the Flag

After successful validation, the program prints:

```c
FUN_140001020("\nCongratulations! Puzzle solved!\n", ...);
```

It then constructs the flag dynamically.

The relevant code is:

```c
bVar4 = 0x46;
lVar15 = 0;

do {
    uVar12 = (uint)param_3;
    param_3 = (ulonglong)(uVar12 + 1);

    *(byte *)((longlong)&local_118 + lVar15) =
        bVar4 ^ (&DAT_1400035c8)[uVar12 & 0xf];

    bVar4 = (&DAT_1400035a1)[lVar15];
    lVar15 = lVar15 + 1;

} while (bVar4 != 0);
```

The resulting buffer is passed to:

```c
FUN_140001020("Your flag is: %s", puVar14, ...);
```

Static string analysis of the executable also reveals the resulting flag.

---

## 11. Flag

```text
FlagY{7b4e3a2c1d8f9e0a5b6c7d8e9f0a1b2c}
```

---

## 12. Solution Summary

The complete execution path is:

```text
entry()
    │
    ▼
FUN_140001b24()
    │
    ▼
FUN_1400014b0()
    │
    ├── Anti-debugging checks
    │
    ├── Read number 0–255
    │
    ▼
(input × 0xD + 7) ^ 0x42
    │
    ▼
& 0xFF
    │
    ▼
Swap nibbles
    │
    ▼
Must equal 0x37
    │
    ▼
Input = 82
    │
    ▼
Congratulations!
    │
    ▼
Flag construction
    │
    ▼
FlagY{7b4e3a2c1d8f9e0a5b6c7d8e9f0a1b2c}
```

## Final Answer

**Input:**

```text
82
```

**Flag:**

```text
FlagY{7b4e3a2c1d8f9e0a5b6c7d8e9f0a1b2c}
```

### Tools Used

* Ghidra
* Static analysis
* x86-64 decompilation
* Modular arithmetic
* String analysis
