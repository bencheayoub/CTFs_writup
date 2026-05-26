# 🔍 GUI I — Malware Reverse Engineering Challenge

## 📌 Challenge Overview

|Category|Level|Tries|Solved|Points|
|---|---|---|---|---|
|Malware Reverse Engineering|Easy|1634|936|50|

> **Challenge Description**  
> The correct input is the flag, formatted as `flag{xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx}`

---

## 🧠 Solution Approach

### 1. Understanding the Target

We are given a Windows executable: `gui.exe`.  
The goal is to find the correct input that produces the flag.

### 2. Initial Analysis with ILSpy

Opening `gui.exe` in **ILSpy** (a .NET decompiler) reveals the application is written in C# / Windows Forms.

Navigating through the decompiled code:

- `GUI` → `WindowsFormsApplication2` → `Form1`

### 3. The Core Logic

Inside `Form1`, we find the `button1_Click` event handler — this is executed when the user clicks a button in the GUI.

Here's the decompiled code (cleaned up):

```csharp
private void button1_Click(object sender, EventArgs e)
{
    CheckBox[] checkBoxes = new CheckBox[8] {
        checkBox1, checkBox2, checkBox3, checkBox4,
        checkBox5, checkBox6, checkBox7, checkBox8
    };

    int sum = 0;
    int index = 0;

    foreach (CheckBox cb in checkBoxes)
    {
        if (cb.Checked && checkBoxes[index].Checked)
        {
            sum += (int)Math.Pow(2.0, index);
        }
        index++;
    }

    label4.Text = sum.ToString();

    string[] numbers = label3.Text.Split(' ');
    int expected = int.Parse(numbers[current]) + 10;

    if (expected == sum)
    {
        label2.Text += (char)sum;
        current++;
    }
}
```

### 4. Hidden Data

Looking through the form's initialization code (`InitializeComponent`), we notice:

```csharp
label3.Text = "92 98 87 93 113 95 105 85 106 94 95 105 85 89 87 91 105 87 104 85 89 95 102 94 91 104 53 115";
label3.Visible = false;  // Hidden from the GUI
```

So `label3` contains a hidden sequence of numbers.

---

### 5. Understanding the Transformation

From the button click logic:

- The user selects checkboxes → their checked state is converted to a binary-like sum.
- Each correct checkbox combination produces a number `sum`.
- That `sum` is compared to:  
    `(label3 number at current index) + 10`

If they match, the `sum` is appended as a **character** to `label2.Text` (the flag).

Thus, the flag is built character by character.

---

### 6. Reversing the Logic

We don't need to brute-force checkboxes.  
We simply:

1. Take each number from `label3`
2. Add 10 to it
3. Convert the result to a **character** (ASCII/Unicode)

---

### 7. Extracting the Flag

Using CyberChef or a small script:

**Step 1 — Original numbers**

```
92 98 87 93 113 95 105 85 106 94 95 105 85 89 87 91 105 87 104 85 89 95 102 94 91 104 53 115
```

**Step 2 — Add 10 to each**

```
102 108 97 103 123 105 115 95 116 104 105 115 95 99 97 101 115 97 114 95 99 105 112 104 101 114 63 125
```

**Step 3 — Convert from decimal to text**

```
flag{is_this_caesar_cipher?}
```

---

## ✅ Final Flag

```
flag{is_this_caesar_cipher?}
```

---

## 🧰 Tools Used

- [ILSpy](https://github.com/icsharpcode/ILSpy) — .NET decompiler
- [CyberChef](https://gchq.github.io/CyberChef/) — for quick decoding

---

## 📝 Notes

- The challenge name "GUI I" hints that the flag is hidden behind GUI interactions.
- The checkbox logic is a red herring  you never need to solve it manually.
- The hidden label (`label3`) is the real key.
- Adding 10 to each number reverses the check in the button click.

---

## 📁 Repository Structure

```
📁 challenge/  
└── gui.exe # Original challenge binary

📁 sol/  
├── README.md # This write-up  
└── solution.py # Python script to extract flag
```

---

##  Solve Script

```python
data = "92 98 87 93 113 95 105 85 106 94 95 105 85 89 87 91 105 87 104 85 89 95 102 94 91 104 53 115"
numbers = list(map(int, data.split()))
flag_chars = [chr(n + 10) for n in numbers]
print(''.join(flag_chars))
```

Output:

```
flag{is_this_caesar_cipher?}
```

---

## 🏁 Conclusion

A clean and easy reverse engineering challenge  simple static analysis reveals the flag without needing to run the binary. Always check for hidden data in UI elements!
