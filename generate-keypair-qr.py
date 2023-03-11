#!/usr/bin/python3
"""
Generate an SSH keypair, outputting a QR code in a Postscript format to stdout.

You can pipe this directly to a printer to avoid saving the private key to disk, eg:

`python3 generate-keypair-qr.py ed25519 | nc 192.168.0.92 9100`

The generated public keys will be appended to `public_keys.out`.

"""


import glob
import os
import tempfile
import subprocess
import sys

# Eg: ed25519 or rsa
key_type = sys.argv[1]

# Allocate a temporary file to get a name
f = tempfile.NamedTemporaryFile()
f.close()

# Create a fifo in its place
os.umask(0o077)
os.mkfifo(f.name)

# Generate a keypair, with the private key going into the FIFO
p = subprocess.Popen(["ssh-keygen", "-q", "-t", key_type, "-N", "", "-f", f.name], stdout=subprocess.DEVNULL, stdin=subprocess.PIPE)

# Agree to overwrite the output file
p.stdin.write(b"y\n")
p.stdin.flush()

# Read in the keys (from FIFO and disk)
private_key = open(f.name, "r").read()
public_key = open(f.name + ".pub", "r").read()

# Remove the FIFO and public key
os.unlink(f.name)
os.unlink(f.name + ".pub")

# RSA keys only fit if we lower the eclevel
eclevel = "L" if len(private_key)>1000 else "M"

keys = private_key + "\n\n" + "\n".join(public_key[i:i+100] for i in range(0, len(public_key), 100))

sys.stdout.write(
    "\n".join(
        open(i).read() for i in sorted(glob.glob("postscriptbarcode/*.ps"))
    ) + """

%!PS

<< /PageSize [595 842] >> setpagedevice

50 570 moveto (""" + private_key + """) (width=3 height=3 eclevel=""" + eclevel + """)
/qrcode /uk.co.terryburton.bwipp findresource exec

400 678 moveto (""" + public_key + """) (width=1.5 height=1.5 eclevel=""" + eclevel + """)
/qrcode /uk.co.terryburton.bwipp findresource exec

/mono findfont 8 scalefont setfont
""" + "\n".join(f"50 {510 - i*10} moveto ({line}) show" for i,line in enumerate(keys.split("\n"))) + """

showpage
%%EOF
""")

open("public_keys.out", "a").write(public_key)

