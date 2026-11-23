# Debugger 0

## Challenge Information

- **Category:** Reverse Engineering / Debugging
- **Level:** Beginner
- **Platform:** CYLAB Academy
- **Tools:** GDB, GEF, GCC
- **Concepts:** Memory inspection, Little Endian, GDB debugging

## Description

The challenge provides a C program containing the constant `0x2262c96b` inside the `main` function.

The objective is to inspect the memory byte-by-byte using GDB and retrieve the four bytes in their actual memory order to construct the flag.

## Solution

### 1. Disassemble main

Start GDB:

```bash
gdb ./debugger0_c
```

Set a breakpoint at `main` and execute the program:

```gdb
break main
run
```

Disassemble the function:

```gdb
disassemble main
```

The important instruction is:

```asm
0x401115 <main+000f> mov DWORD PTR [rbp-0x4], 0x2262c96b
```

This instruction stores the 32-bit constant `0x2262c96b` at the memory address `[rbp-0x4]`.

### 2. Inspect memory

Initially, examining the memory showed four zero bytes because the store instruction had not executed yet.

```gdb
x/4xb $rbp-4
```

To execute the instructions one by one, use:

```gdb
ni
ni
```

Now the constant has been stored in memory.

Examine it again:

```gdb
x/4xb $rbp-4
```

Output:

```text
0x7fffffffd4cc:  0x6b  0xc9  0x62  0x22
```

### 3. Understand the result

The original integer is:

```text
0x2262c96b
```

My machine uses the **Little Endian** byte ordering.

In Little Endian, the least significant byte is stored at the lowest memory address.

Therefore:

| Memory order | Byte |
|---|---|
| Byte 1 | `0x6b` |
| Byte 2 | `0xc9` |
| Byte 3 | `0x62` |
| Byte 4 | `0x22` |

The bytes must be concatenated in the exact order returned by GDB.

## Flag

```text
academy{0x6bc96222}
```

## Key Takeaways

- `disassemble main` helps identify instructions and memory locations.
- `ni` executes the next instruction without stepping into function calls.
- `x/4xb address` examines four individual bytes in hexadecimal.
- Little Endian stores the least significant byte first.
- Always ensure the instruction has executed before inspecting the memory it modifies.
