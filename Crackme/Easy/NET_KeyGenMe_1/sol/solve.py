#!/usr/bin/env python3
"""Keygen for ".NET KeyGenMe #1" by 7ssX.

Logic recovered from Form1.Button1_Click / Form1.enc():
    serial = Base64( TripleDES-ECB-PKCS7( ASCII(username), key = MD5(SECRET) ) )
"""
import sys, base64, hashlib
from Crypto.Cipher import DES3
from Crypto.Util.Padding import pad

SECRET = "wtMd3x6ucb16w9P9BBPj5qoHKPCq0MIy"   # the ldstr found in Button1_Click

def keygen(username: str) -> str:
    key = hashlib.md5(SECRET.encode("ascii")).digest()          # 16 bytes -> 2-key 3DES
    cipher = DES3.new(key, DES3.MODE_ECB)                       # CipherMode 2 = ECB
    ct = cipher.encrypt(pad(username.encode("ascii"), 8))       # PKCS7 (the .NET default)
    return base64.b64encode(ct).decode()

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else input("Username: ")
    print(f"Username: {name}\nSerial  : {keygen(name)}")
