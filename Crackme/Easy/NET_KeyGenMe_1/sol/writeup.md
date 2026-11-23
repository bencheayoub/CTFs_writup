# .NET KeyGenMe #1 (by 7ssX)

- **Type:** Keygenme (reverse engineering)
- **Target:** `.NET KeyGenMe #1.exe` (PE32, .NET / VB.NET WinForms, assembly `CrackMe.exe`)
- **Goal:** Write a keygen. A valid Username/Serial pair shows `Yup, you did it! Go write a KeyGen!`
- **Flag:** none embedded in the binary. Solved = a valid pair accepted by the program.

> Note: the logic below was recovered by static analysis (IL disassembly) only.
> I did not run the .exe while writing this, so confirm a pair in the real program.

## 1. Recon

```
$ file ".NET KeyGenMe #1.exe"
PE32 executable (GUI) Intel 80386 Mono/.Net assembly, for MS Windows
```

A .NET assembly, so use dnSpy / ILSpy / dotPeek (or `monodis`).
One form: `CrackMe.Form1` with `MD5Hash`, `enc` and `Button1_Click`.

## 2. Strings (#US heap)

| String | Meaning |
|---|---|
| `wtMd3x6ucb16w9P9BBPj5qoHKPCq0MIy` | hardcoded secret passed to `enc` |
| `Yup, you did it! Go write a KeyGen!` | success message |
| `Sorry, try again!` | failure message |

## 3. Check logic (`Button1_Click`)

```
if TextBox2.Text == enc(TextBox1.Text, "wtMd3x6ucb16w9P9BBPj5qoHKPCq0MIy")
    -> success
else
    -> "Sorry, try again!"
```

TextBox1 = Username, TextBox2 = Serial.

## 4. `enc(input, key)`

1. 3DES key = `MD5(ASCII(key))` (16 bytes, so two-key 3DES)
2. `Mode = 2` which is `CipherMode.ECB`
3. Padding = default PKCS7
4. Encrypt `ASCII(input)`, return Base64

So: `serial = Base64( 3DES_ECB_PKCS7( ASCII(username), MD5(secret) ) )`

`MD5("wtMd3x6ucb16w9P9BBPj5qoHKPCq0MIy") = e9cab1967e0c7b441b8f360ecdb244fe`

## 5. Solve

```
pip install pycryptodome
python3 solve.py 7ssX
```

| Username | Serial |
|---|---|
| `7ssX` | `CMcSu4t6vDQ=` |
| `Atomic` | `b+CD81ZFWMY=` |
| `test` | `kb8qGO71sow=` |

### No-code alternative (CyberChef)

1. Input: username
2. `Triple DES Encrypt`: key `e9cab1967e0c7b441b8f360ecdb244fe` (Hex), IV empty, Mode ECB, Input Raw, Output Raw
3. `To Base64`

## Takeaways

- Hardcoded secret + standard crypto, so the keygen is a straight reimplementation.
- .NET has no obfuscation here, so a decompiler shows everything.
