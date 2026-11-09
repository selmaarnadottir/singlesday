# Dulkóðar JSON-skrá með lykilorði (PBKDF2-SHA256 + AES-256-GCM) fyrir Singles Day mælaborðið.
# Notkun: python3 enc.py <lykilorð> <inn.json> <út.enc.json>
import sys,os,json,base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
pw,src,dst=sys.argv[1:4]; N=600000
salt,iv=os.urandom(16),os.urandom(12)
key=PBKDF2HMAC(algorithm=hashes.SHA256(),length=32,salt=salt,iterations=N).derive(pw.strip().lower().encode())
ct=AESGCM(key).encrypt(iv,open(src,"rb").read(),None)
b=lambda x:base64.b64encode(x).decode()
json.dump({"n":N,"s":b(salt),"iv":b(iv),"ct":b(ct)},open(dst,"w"))
print("ok",dst)
