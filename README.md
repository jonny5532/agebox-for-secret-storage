# Managing secrets in a git repository using agebox

## 1. Generating recovery keypairs

It is worth creating a recovery key so that you can decrypt your data even if
you have lost access to your usual keys.

To reduce the risk of the recovery key being compromised, we can print it out
on paper without storing a digital copy.

The `generate-keypair-qr.py` script will use `ssh-keygen` to generate a keypair,
avoiding saving the private key to disk, output it as a QR code to stdout, which
you can then send to the JetDirect port on a local laser printer using netcat.

`python3 generate-keypair-qr.py ed25519 | nc <printer ip> 9100`

There's no guarantee that the printer won't store the job in persistent memory, 
or that the plaintext won't end up in your machine's swap file, but it's as good
as we can easily manage. Also be aware that we're sending it unencrypted over
the local network - it would be safer to pipe it over USB or parallel.

