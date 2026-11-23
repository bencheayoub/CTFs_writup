enc = "慣慤敭祻ㄶ形楴獟楮獴㌴摟潦弸強㤰扡㌷敽"

def decrypt(enc):
    dec = ''
    for c in enc:
        dec += chr(ord(c) >> 8)      # high byte -> first char
        dec += chr(ord(c) & 0xFF)    # low byte  -> second char
    return dec

print(f'Decrypted flag: {decrypt(enc)}')
