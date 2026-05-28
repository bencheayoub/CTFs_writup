data = "92 98 87 93 113 95 105 85 106 94 95 105 85 89 87 91 105 87 104 85 89 95 102 94 91 104 53 115"
numbers = list(map(int, data.split()))
flag_chars = [chr(n + 10) for n in numbers]
print(''.join(flag_chars))