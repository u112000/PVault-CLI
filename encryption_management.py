#===========================================================
# Script Name: encryption_management.py +
# Author: u112000
# Created: 2025-11-02
# Last Updated: 2025-11-02
# Version: 1.0.0
# Description:
#     The program was created by constant curiosity and persistence to complete old forgotten projects.
#     It serves as a POC of what can/could be created with just as little as an "if...else:" statement.
#     for the curious minds..
#===========================================================


#! python3

import os, sys
import time
import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class CryptographyLogic:
    def __init__(self):
        self.state = True
        self.keyspath = os.path.join(os.getcwd(), 'keys', 'keys_data')
        if os.path.isfile(self.keyspath) != True:
            self.state = False
        else:
            file_data = open(self.keyspath, 'rb').readlines()
            self.key = bytes.fromhex(file_data[0].decode())
            self.nonce = bytes.fromhex(file_data[1].decode())
            self.aead = bytes.fromhex(file_data[2].decode())
            self.locker = AESGCM(self.key)

    def reconciliation(self, OPType):
        from PVault import printer
        if OPType == 'Key_status':
            printer(f'Decryption failed due to mismatched or missing key file.\nRestore the original key file to regain access to existing data.\nA debug log has been created for reference.', 'Key File Mismatch Detected')
            sys.exit(1)
        elif OPType == 'cryptography_failure':
            printer(f'The decryption key file could not be located.\nUse the key generation command to create a new key file,\n or restore the original keys to access existing encrypted data.', 'Decryption Failure')
            sys.exit(1)

    def decryption(self, data):
        if self.state == False:
            self.reconciliation('Key_status')
        data = bytes.fromhex(data)
        try:
            decrypted_data = self.locker.decrypt(self.nonce, data, self.aead)
        except Exception as err:
            with open(f'{time.strftime("%c", time.localtime())}-crash_log.txt', 'wt') as f:
                f.write(str(err))
            self.reconciliation('cryptography_failure')
            raise Exception()
        else:
            return decrypted_data.decode()

    def encryption(self, data):
        if self.state == False:
            self.reconciliation('Key_status')
        data = data.encode()
        try:
            return self.locker.encrypt(self.nonce, data, self.aead).hex()
        except Exception as err:
            with open(f'{time.strftime("%c", time.localtime())}-crash_log.txt', 'wt') as f:
                f.write(str(err))
            self.reconciliation('cryptography_failure')
            raise Exception()
    def Generate_DBkeys(self):
        from PVault import printer
        if not os.path.isdir(os.path.dirname(self.keyspath)):
            printer(f"The expected key storage folder was not found at:\n[bold yellow]{os.path.dirname(self.keyspath)}[/bold yellow]\n\nCreate this folder before generating new keys.", 'Keys Directory Missing')
            sys.exit(1)
        if os.path.isfile(self.keyspath):
            printer('A key file already exists in the keys directory.\nTo generate new keys, delete the existing file manually.\nProceed with caution — all data encrypted with old keys will become inaccessible', 'Existing Key File Detected')
            sys.exit(1)
        KEY = secrets.token_bytes(32).hex()
        NONCE = secrets.token_bytes(16).hex()
        AEAD = secrets.token_bytes(16).hex()
        with open(self.keyspath, 'wt', encoding='utf-8') as f:
            f.write(KEY+'\n')
            f.write(NONCE+'\n')
            f.write(AEAD+'\n')
            f.write('\n\n\n!!! WARNING: Do not overwrite key file unless you intend to reset the vault.!!!\n\n!!! The key file can be carried around with you. as long as you can provide that same file when interacting with the program otherwise all previous data is unaccessible.\nLOSING or DELETING the key file will make encrypted data unrecoverable!!!')
        self.state = True
        return f''' • New Cryptographic Keys Generated:
 • Keys successfully created and stored at: [bold yellow]{self.keyspath}[/bold yellow]

[+] [dim]Key (32 bytes):[/dim] [bold cyan]{KEY}[/bold cyan]
[+] [dim]Nonce (16 bytes):[/dim] [bold cyan]{NONCE}[/bold cyan]
[+] [dim]Associated Tag (16 bytes):[/dim] [bold cyan]{AEAD}[/bold cyan]
'''
