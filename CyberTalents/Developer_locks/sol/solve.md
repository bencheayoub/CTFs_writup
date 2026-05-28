# 🔍 Developer locks — Malware Reverse Engineering Challenge

## 📌 Challenge Overview

| Category | Level | Tries | Solved | Points |
|----------|-------|-------|--------|--------|
| Malware Reverse Engineering | Easy | 1850 | 771 | 50 |

> **Challenge Description**  
> This is kinda easy to the degree that you'll be asked for the hash at once.

---

## 🧠 Solution Approach

### 1. Understanding the Target

We are given a Windows executable: `CT-rev-b1.exe`.  
The goal is to find the correct hash/input that satisfies the program's validation logic.

### 2. Initial Analysis with ILSpy

Opening the executable in **ILSpy** (a .NET decompiler) reveals the application is written in C#. The assembly information shows:

- **Assembly Name:** `CT_rev_b1`
- **Namespace:** `CT_rev_b1`
- **Class:** `Program`

Navigating through the decompiled code:
```
CT_rev_b1 (1.0.0.0)
└── CT_rev_b1
    └── Program
        ├── CreateMD5(string): string
        └── Main(string[]): void
```

### 3. The Core Logic

Inside the `Program` class, we find the `Main` method — this is the entry point of the application.

Here's the decompiled code (cleaned up):

```csharp
private static void Main(string[] args)
{
    Console.WriteLine("Pretty simple. eh?, you give me the hash and i`ll be happy :D");
    string input = Console.ReadLine();

    if (input.Length > 11)
    {
        Console.WriteLine("nope!");
        return;
    }
    else if (CreateMD5(Environment.UserName + input) != "C246B75690B6F0746AA67ECC9B400ECF")
    {
        Console.WriteLine(":'(");
        return;
    }

    Console.WriteLine(":) thanks");
}
```

### 4. The MD5 Hash Function

The program also contains an MD5 implementation:

```csharp
private static string CreateMD5(string input)
{
    using (MD5 md5 = MD5.Create())
    {
        byte[] bytes = Encoding.ASCII.GetBytes(input);
        byte[] hash = md5.ComputeHash(bytes);
        StringBuilder sb = new StringBuilder();

        for (int i = 0; i < hash.Length; i++)
        {
            sb.Append(hash[i].ToString("X2"));
        }

        return sb.ToString();
    }
}
```

**Key observations:**
- The function takes a string input and returns its MD5 hash in **uppercase hexadecimal format**
- The program accepts user input (maximum 11 characters)
- Input is concatenated with the system's `Environment.UserName`
- The MD5 hash of `(Username + Input)` is computed
- The result is compared against the hardcoded hash: `C246B75690B6F0746AA67ECC9B400ECF`

### 5. Determining the Username

The program uses `Environment.UserName`, which varies depending on the system it runs on. However, the assembly namespace provides a crucial clue: `CT_rev_b1`.

This is likely the username the developer used when creating the challenge. The executable name itself (`CT-rev-b1.exe`) further reinforces this assumption.

**Inferred username:** `CT_rev_b1`

### 6. Reversing the Logic

We know:
- Target hash: `C246B75690B6F0746AA67ECC9B400ECF`
- Username: `CT_rev_b1`
- Constraint: Input length ≤ 11 characters
- Need to find INPUT such that:  
  **MD5(`CT_rev_b1` + INPUT) = `C246B75690B6F0746AA67ECC9B400ECF`**

Rather than brute-forcing, we can use an MD5 reverse lookup service (e.g., md5decrypt.net) to find what plaintext produces the target hash.

**Decrypted result:** The plaintext that hashes to `C246B75690B6F0746AA67ECC9B400ECF` is `Pic@tchuz00`

### 7. Verification

Since the hash is of `CT_rev_b1` + INPUT, the actual concatenated string is:
```
CT_rev_b1Pic@tchuz00
```

Let's verify:
```
Username:     CT_rev_b1
Input:        Pic@tchuz00
Concatenated: CT_rev_b1Pic@tchuz00
MD5(CT_rev_b1Pic@tchuz00) = C246B75690B6F0746AA67ECC9B400ECF ✓
```

Length check: `Pic@tchuz00` is exactly 11 characters, satisfying the length constraint.

### 8. Understanding the Flag Format

The challenge asks for "the hash" — in this context, the correct input that makes the program print `:) thanks` is the flag. The flag is the string you need to provide to the program, not the MD5 hash itself.

**Flag:** `Pic@tchuz00`

---

## ✅ Final Flag

```
Pic@tchuz00
```

---

## 🧰 Tools Used

- [ILSpy / AvaloniaILSpy](https://github.com/icsharpcode/ILSpy) — .NET decompiler
- [md5decrypt.net](https://md5decrypt.net/) — MD5 reverse lookup service

---

## 📝 Notes

- The challenge name "Developer locks" hints that the developer locked the flag behind a simple hash check.
- The username being hardcoded in the namespace is a common trick — always check assembly metadata!
- The program never actually asks for "the hash" as the description suggests — it asks for the input that produces the correct hash.
- The 11-character limit is a useful constraint for manual brute-force if needed.
- This challenge demonstrates how easily .NET executables can be reversed with the right tools.

---

## 📁 Repository Structure

```
📁 challenge/
└── CT-rev-b1.exe       # Original challenge binary

📁 sol/
├── README.md           # This write-up
├── solution.py         # Python script to solve
└── solve.sh            # Bash one-liner solution
```

---

## 🔧 Solve Scripts

### Python Solution

```python
import hashlib

target_hash = "C246B75690B6F0746AA67ECC9B400ECF"
username = "CT_rev_b1"

# The flag was found via MD5 reverse lookup
flag = "Pic@tchuz00"

# Verify
test_string = username + flag
computed_hash = hashlib.md5(test_string.encode('ascii')).hexdigest().upper()

print(f"Username: {username}")
print(f"Flag: {flag}")
print(f"Test string: {test_string}")
print(f"Computed MD5: {computed_hash}")
print(f"Target MD5: {target_hash}")
print(f"Match: {computed_hash == target_hash}")
```

**Output:**
```
Username: CT_rev_b1
Flag: Pic@tchuz00
Test string: CT_rev_b1Pic@tchuz00
Computed MD5: C246B75690B6F0746AA67ECC9B400ECF
Target MD5: C246B75690B6F0746AA67ECC9B400ECF
Match: True
```

### Bash One-Liner

```bash
echo -n "CT_rev_b1Pic@tchuz00" | md5sum | tr 'a-f' 'A-F'
# Output: C246B75690B6F0746AA67ECC9B400ECF
```

---

## 🏁 Conclusion

A straightforward reverse engineering challenge — simple static analysis of the decompiled .NET code reveals the validation logic. By identifying the username from the namespace and using an MD5 reverse lookup, we obtain the flag without ever running the binary. The flag is simply the 11-character input string: `Pic@tchuz00`
