# 🌙 Good9 — Android RE CTF Write-up

> **Category:** Android Reverse Engineering
> **Flag:** `THEM?!CTF{D0_Y0u_H4v3_A_G00d_T1m3?}`
> **Tools:** `apktool` · `radare2` · `adb` · `python3`

---

## Overview

nightnight is a native-heavy Android RE challenge. The Java layer is a thin façade — all meaningful logic lives inside a single shared library, `libsilence.so`, which implements a modified SHA-256 cipher with non-standard IVs, a two-table XOR key obfuscation scheme, and runtime anti-analysis checks.

---

## Step 1 — Initial Reconnaissance

Unpack the APK with apktool:

```bash
apktool d nightnight.apk -o out/
```

The asset directory immediately draws attention:

```
out/assets/
├── 218a844...   (2.3 KB — encrypted payload)
├── b86e8f6...   (40 bytes — key material)
└── dexopt/

out/lib/x86_64/
└── libsilence.so
```

The 40-byte asset is a strong hint — it matches the expected key size referenced in the Java source.

---

## Step 2 — Static Analysis: Java Layer

Decompiling the bytecode reveals a minimal Java surface that delegates everything to JNI:

```java
// MainActivity.java
byte[] flag = Night.prepareVM(classLoader, assets)
                   .getFlag(Night.getKey());
Log.i("Good Night", "Flag is " + new String(flag, UTF_8));
```

```java
// Night.java
public static byte[] Key = new byte[40];

public static native VM     prepareVM(ClassLoader cl, AssetManager am);
public static native byte[] bridge(byte[] input);
public static native void   loadKey(AssetManager am);
```

> **Note:** All three native methods are registered dynamically via `RegisterNatives`, meaning no predictable JNI symbol names exist in the export table. Resolving actual function addresses requires analysing `JNI_OnLoad`.

---

## Step 3 — Native Library: Symbol Recon

```bash
nm -D out/lib/x86_64/libsilence.so
```

| Symbol                        | Implication                                                       |
| ----------------------------- | ----------------------------------------------------------------- |
| `ptrace`                      | Anti-debugging — detects attached debuggers                       |
| `AAsset_open` / `AAsset_read` | Direct NDK asset access, bypassing Java                           |
| `JNI_OnLoad`                  | Only exported JNI entry point — all methods registered at runtime |

---

## Step 4 — JNI_OnLoad: Resolving the Dispatch Table

Disassembling `JNI_OnLoad` in radare2 exposes the `RegisterNatives` call, which maps method names to native addresses at runtime:

```bash
r2 -A out/lib/x86_64/libsilence.so
[0x00001000]> pdf @ sym.JNI_OnLoad
```

| Offset   | Registered Method | Notes                         |
| -------- | ----------------- | ----------------------------- |
| `0x2630` | `getFlag`         | Returns decrypted flag bytes  |
| `0x3e50` | `bridge`          | Intermediate transform        |
| `0x4c40` | `loadKey`         | Key construction + asset read |

---

## Step 5 — loadKey: Key Recovery

The function at `0x4c40` builds the first 18 bytes of the key statically by XOR-ing two hardcoded lookup tables embedded in the binary:

```asm
movzx eax, byte [0x00000cc0]   ; Table A[i]
xor   al,  byte [0x00000ce0]   ; Table B[i]
mov   byte [rbp - 0x30], al    ; Key[i]
; ... repeated for 18 iterations (mov esi, 0x12)
```

Extracting both tables and XOR-ing them in Python:

```python
data  = open("libsilence.so", "rb").read()
pairs = [(0xcc0 + i, 0xce0 + i) for i in range(18)]
key   = bytes(data[a] ^ data[b] for a, b in pairs)
print(key)
# b'nightnight{silent}'
```

The remaining 22 bytes are loaded at runtime directly from the asset file via `AAsset_read`, completing the full 40-byte key.

---

## Step 6 — Anti-Analysis Measures

Identified in `fcn.000050e0`:

| Technique          | Target File         | Method                                                           |
| ------------------ | ------------------- | ---------------------------------------------------------------- |
| Debugger detection | `/proc/self/status` | Checks `TracerPid` field — non-zero means a debugger is attached |
| Frida detection    | `/proc/self/maps`   | Scans for strings: `Frida`, `frida`, `gadget`                    |

> **Important:** Both checks target ARM devices. The **x86_64** build present in this APK does not enforce them with the same reliability — an exploitable inconsistency.

---

## Step 7 — Cryptographic Core: Modified SHA-256

`fcn.00004a20` is a custom SHA-256 implementation. It uses the standard K-constants and compression function structure, but replaces the initial hash values with non-standard IVs and applies modified rotation constants in the message schedule:

```python
# Standard SHA-256 IVs (RFC 6234):
# H = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, ...]

# Challenge IVs (non-standard):
H = [0x30303030, 0x30303030, 0x30303030, 0x30303030,
     0x10101010, 0x10101010, 0x10101010, 0x10101010]
```

This deviation from the standard produces a completely different digest for any given input, making all standard SHA-256 libraries useless without patching the IV values.

---

## Step 8 — Dynamic Analysis: Flag Extraction

Rather than reimplementing the custom hash variant from scratch, we ran the application on a real device. The flag is printed in plaintext to logcat immediately after decryption — a detail visible from the Java layer static analysis in Step 2.

```bash
adb install nightnight.apk
adb shell am start -n lab.nightjar/.MainActivity
adb logcat | grep "good Night"
```

```
I Good Night: Flag is THEM?!CTF{D0_Y0u_H4v3_A_G00d_T1m3?}.
```

**Flag:** `THEM?!CTF{D0_Y0u_H4v3_A_G00d_T1m3?}`

---

## Key Takeaways

### Technical

* Custom SHA-256 IV substitution produces a non-standard digest, defeating off-the-shelf hash tools
* The partial key `nightnight{silent}` is obfuscated via a two-table XOR scheme embedded in the binary
* Dynamic `RegisterNatives` registration hides all meaningful function names from the export table
* Anti-Frida / anti-debug checks are architecture-specific — weaker on x86_64 than on ARM

### Methodology

* Always check logcat output before investing time in full static analysis
* The Java layer often exposes log calls that print secrets in plaintext — read it first
* A native library performing its own `AAsset_read` calls is a strong indicator of key material stored in assets
* When custom crypto is involved, running the binary dynamically is usually faster than reimplementing the algorithm

---

*Write-up by Atomic*
