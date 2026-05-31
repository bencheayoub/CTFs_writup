# I love this guy

| Field    | Details                     |
| -------- | --------------------------- |
| Category | Malware Reverse Engineering |
| Level    | Medium                      |
| Points   | 100                         |
| Solves   | 427 / 574                   |

## Description

> Can you find the password to obtain the flag?

A compiled .NET WPF application prompts the user for a password. The goal is to recover the password and the flag through static analysis, no execution required.

---

## Tools

- [AvaloniaILSpy](https://github.com/icsharpcode/AvaloniaILSpy) — .NET decompiler

---

## Solution

### 1. Locating the logic

Opening the binary in AvaloniaILSpy and navigating to:

```
ScrambledEgg → FirstWPFApp → MainWindow
```

We find a static character alphabet defined at class level:

```csharp
using Letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ{}_".ToCharArray();
```

This gives a 29-character lookup table:

| Index | 0   | 1   | 2   | …   | 25  | 26  | 27  | 28  |
| ----- | --- | --- | --- | --- | --- | --- | --- | --- |
| Char  | A   | B   | C   | …   | Z   | {   | }   | _   |
|       |     |     |     |     |     |     |     |     |

---

### 2. Recovering the password

The decompiled C# shows a 5-character string built from `Letters` indices:

```csharp
string value = new string(new char[5]
{
    Letters[5],   // F
    Letters[14],  // O
    Letters[13],  // N
    Letters[25],  // Z
    Letters[24]   // Y
});
```

**Password: `FONZY`**

---

### 3. Recovering the flag

If the user input matches `value`, a `MessageBox` displays an 18-character flag, also built from `Letters`:

```csharp
MessageBox.Show(new string(new char[18]
{
    Letters[5],   // F
    Letters[11],  // L
    Letters[0],   // A
    Letters[6],   // G
    Letters[26],  // {
    Letters[8],   // I
    Letters[28],  // _
    Letters[11],  // L
    Letters[14],  // O
    Letters[21],  // V
    Letters[4],   // E
    Letters[28],  // _
    Letters[5],   // F
    Letters[14],  // O
    Letters[13],  // N
    Letters[25],  // Z
    Letters[24],  // Y
    Letters[27]   // }
}));
```

---
### The Solver Script:

```python
def decode(indices):
    letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ{}_")
    return "".join(letters[i] for i in indices)

# Password
print(decode([5, 14, 13, 25, 24]))          # FONZY

# Flag
print(decode([5,11,0,6,26,8,28,11,14,21,4,28,5,14,13,25,24,27]))  # FLAG{I_LOVE_FONZY}
```

### output

```
FLAG{I_LOVE_FONZY}
```

---

## Takeaway

The application performs no encryption or obfuscation, both the password and the flag are assembled directly from a plaintext alphabet array visible in the IL. A single pass through a .NET decompiler is sufficient to recover everything statically.
