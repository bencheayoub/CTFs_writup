def decode(indices):
    letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ{}_")
    return "".join(letters[i] for i in indices)

# Password
print(decode([5, 14, 13, 25, 24]))          # FONZY

# Flag
print(decode([5,11,0,6,26,8,28,11,14,21,4,28,5,14,13,25,24,27]))  # FLAG{I_LOVE_FONZY}
