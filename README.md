Использование в терминале:
```
$ python main.py
What should we encrypt/decrypt?
1. file
2. input
Choose an option: 1
1. vadim-pcbc.enc
2. vadim.txt     
Choose file: 1   
Use key and salt from files?
1. yes
2. no
Choose an option: 1
Choose key file:
1. new_key.bin  
2. vadim_key.bin
Choose file: 1  
Choose salt file:
1. new_salt.bin  
2. vadim_salt.bin
Choose file: 1   

KEY: b'\x85YW\xb8\xcb\x15:^\xa2\xac\x03\xe8\xd3\n\xc0\xdf'
SALT: b"\xfc\x7f\x1fof\xf7\xbf\xac\x19V\xc4&\x05'\x14\x9e"

Action
1. encrypt
2. decrypt
Choose an option: 1
Choose method of AES encryption:
1. cbc
2. pcbc
3. cfb
4. ofb
5. ctr
Choose an option: 4
Output should be in:
1. file
2. terminal
Choose an option: 1
DEBUG: vadim-pcbc.enc, vadim-pcbc
Output file saved successfully in ./output_files/vadim-pcbc-ofb.enc
Success
```
