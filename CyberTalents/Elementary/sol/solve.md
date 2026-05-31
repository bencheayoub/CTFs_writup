# Elementary — CTF Writeup

| Field       | Details                        |
|-------------|-------------------------------|
| **Name**    | Elementary                    |
| **Category**| Malware Reverse Engineering   |
| **Level**   | Medium                        |
| **Points**  | 100                           |
| **Solves**  | 461 / 534                     |

---

## Description

> "Here we've prepared a simple program, crack me if you can."

A Linux x86-64 binary that prompts for a **Username** and a **Password**. The goal is to find the correct credentials.

---

## Approach

### 1. Static Analysis with IDA Pro

Opening the binary in IDA Pro and decompiling `main()` revealed the following logic:

```c
__int64 __fastcall main(int a1, char **a2, char **a3)
{
  char buf[9]; // username buffer
  char v5[9];  // password buffer
  unsigned __int64 v6;

  v6 = __readfsqword(0x28u); // stack canary
  buf[8] = 0;
  v5[8] = 0;

  puts("Username: ");
  read(0, buf, 8uLL);
  puts("Password: ");
  read(0, v5, 8uLL);

  if ( !(unsigned int)sub_79A(buf, v5) )
    sub_816(buf, v5);   // wrong credentials path
  sub_803(buf, v5);     // correct credentials path

  return 0LL;
}
```

**Key observations:**
- Username and password are each limited to **8 bytes**.
- The validation happens inside `sub_79A`.

---

### 2. Analyzing the Validation Function

Decompiling `sub_79A`:

```c
_BOOL8 __fastcall sub_79A(__int64 a1, const char *a2)
{
  return strcmp(a2, s2) == 0;
}
```

The function simply compares the input password (`a2`) against a **hardcoded string `s2`** using `strcmp`. No username check at all — only the password matters.

---

### 3. Extracting the Password

Navigating to the `s2` symbol in IDA's data segment revealed the hardcoded value:

```
s2 = "N1C3Tryy"
```

---

## Solution

| Field        | Value      |
|--------------|-----------|
| **Username** | anything  |
| **Password** | `N1C3Tryy` |

The binary performs **no username validation** — only the password is checked via a plain `strcmp` against a static string stored in the binary's data segment.

---

## Takeaways

- **Never hardcode secrets** in binaries — they are trivially extractable with any decompiler.
- `strcmp` against a static string is one of the weakest validation mechanisms possible; it is both **reversible** and **timing-attack vulnerable**.
- Tools like IDA Pro, Ghidra, or `strings` can recover such credentials in seconds.

---

## Tools Used

- **IDA Pro** — disassembly & decompilation
