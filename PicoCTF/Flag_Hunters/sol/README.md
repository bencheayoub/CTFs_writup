# Flag Hunters

| | |
|---|---|
| **Category** | Reverse Engineering |
| **Difficulty** | Easy |
| **Author** | syreal (picoCTF 2025) |
| **Files** | `lyric-reader.py` |
| **Flag** | `academy{70637h3r_f0r3v3r_ee47a5df}` |

## Challenge

> Lyrics jump from verses to the refrain kind of like a subroutine call. There's a hidden refrain this program doesn't print by default. Can you get it to print it?

The service is a "lyric reader" that prints a song line by line and asks the user to sing along at the `Crowd:` prompt.

## Analysis

The flag is read from `flag.txt` and glued to the **front** of the song:

```python
secret_intro = '''Pico warriors rising, ...
The ether’s ours to conquer, ''' + flag + '\n'

song_flag_hunters = secret_intro + '''
[REFRAIN]
...
'''
```

So the flag sits at line index `0` of `song_lines`, but the reader starts at `[VERSE1]` and never goes back there.

The song is a tiny interpreter. Lines are split on `;` and each piece is treated as an instruction:

| Piece | Effect |
|---|---|
| `REFRAIN` | Saves a return address in the `RETURN` line, jumps to `[REFRAIN]` |
| `CROWD...` | Reads user input and **writes it back into the song** |
| `RETURN <n>` | Jumps to line `n` |
| `END` | Stops |

The bug is the crowd handler:

```python
elif re.match(r"CROWD.*", line):
    crowd = input('Crowd: ')
    song_lines[lip] = 'Crowd: ' + crowd   # user input stored in the program
    lip += 1
```

Our input is stored raw into `song_lines`. The next time that line is executed it is split on `;` again, so a `;` in our input lets us inject our own instructions. This is an injection into the interpreter's own code.

## Exploit

At the first `Crowd:` prompt, enter:

```
;RETURN 0
```

The crowd line now reads `Crowd: ;RETURN 0`. The refrain is called again after the next verse, and this time the line splits into:

1. `Crowd: ` (printed normally)
2. `RETURN 0` (matches `RETURN [0-9]+`, so `lip = 0`)

Execution jumps to line 0, the secret intro, and prints the flag. Since `RETURN 0` sits inside the refrain, it keeps looping and printing until `MAX_LINES` (100) is hit. `Ctrl+C` is fine once the flag shows.

```
$ nc xebec.cylabacademy.net 14688
...
Crowd: ;RETURN 0
...
Pico warriors rising, puzzles laid bare,
Solving each challenge with precision and flair.
With unity and skill, flags we deliver,
The ether’s ours to conquer, academy{70637h3r_f0r3v3r_ee47a5df}
```

## Takeaways

- Never write user input back into data that is later parsed as code or instructions.
- When the target is a mini-interpreter, look for the instruction that jumps (`RETURN n`) and for any place user input reaches the instruction stream.
- The hidden data was only unreachable by control flow, not by access control, so hijacking control flow was enough.

## Fix

Store the crowd input separately from `song_lines`, or strip/escape `;` before storing it.
