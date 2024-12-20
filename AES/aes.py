from AES.consts import s_box, r_con, inv_s_box
from AES.helper_functions import *

class AES:
  global s_box, r_con, inv_s_box
  """
  Class for AES-128 encryption with CBC mode and PKCS#7.

  This is a raw implementation of AES, without key stretching or IV
  management. Unless you need that, please use `encrypt` and `decrypt`.
  """
  rounds_by_key_size = {16: 10, 24: 12, 32: 14}
  def __init__(self, master_key):
      """
      Initializes the object with a given key.
      """
      assert len(master_key) in AES.rounds_by_key_size
      self.n_rounds = AES.rounds_by_key_size[len(master_key)]
      self._key_matrices = self._expand_key(master_key)

  def _expand_key(self, master_key):
      """
      Expands and returns a list of key matrices for the given master_key.
      """
      # Initialize round keys with raw key material.
      key_columns = bytes2matrix(master_key)
      iteration_size = len(master_key) // 4

      i = 1
      while len(key_columns) < (self.n_rounds + 1) * 4:
          # Copy previous word.
          word = list(key_columns[-1])

          # Perform schedule_core once every "row".
          if len(key_columns) % iteration_size == 0:
              # Circular shift.
              word.append(word.pop(0))
              # Map to S-BOX.
              word = [s_box[b] for b in word]
              # XOR with first byte of R-CON, since the others bytes of R-CON are 0.
              word[0] ^= r_con[i]
              i += 1
          elif len(master_key) == 32 and len(key_columns) % iteration_size == 4:
              # Run word through S-box in the fourth iteration when using a
              # 256-bit key.
              word = [s_box[b] for b in word]

          # XOR with equivalent word from previous iteration.
          word = xor_bytes(word, key_columns[-iteration_size])
          key_columns.append(word)

      # Group key words in 4x4 byte matrices.
      return [key_columns[4*i : 4*(i+1)] for i in range(len(key_columns) // 4)]

  def encrypt_block(self, plaintext):
      """
      Encrypts a single block of 16 byte long plaintext.
      """
      assert len(plaintext) == 16

      plain_state = bytes2matrix(plaintext)

      add_round_key(plain_state, self._key_matrices[0])

      for i in range(1, self.n_rounds):
          sub_bytes(plain_state)
          shift_rows(plain_state)
          mix_columns(plain_state)
          add_round_key(plain_state, self._key_matrices[i])

      sub_bytes(plain_state)
      shift_rows(plain_state)
      add_round_key(plain_state, self._key_matrices[-1])

      return matrix2bytes(plain_state)

  def decrypt_block(self, ciphertext):
      """
      Decrypts a single block of 16 byte long ciphertext.
      """
      assert len(ciphertext) == 16

      cipher_state = bytes2matrix(ciphertext)

      add_round_key(cipher_state, self._key_matrices[-1])
      inv_shift_rows(cipher_state)
      inv_sub_bytes(cipher_state)

      for i in range(self.n_rounds - 1, 0, -1):
          add_round_key(cipher_state, self._key_matrices[i])
          inv_mix_columns(cipher_state)
          inv_shift_rows(cipher_state)
          inv_sub_bytes(cipher_state)

      add_round_key(cipher_state, self._key_matrices[0])

      return matrix2bytes(cipher_state)

  def encrypt_cbc(self, plaintext, iv):
      """
      Encrypts `plaintext` using CBC mode and PKCS#7 padding, with the given
      initialization vector (iv).
      """
      assert len(iv) == 16

      plaintext = pad(plaintext)

      blocks = []
      previous = iv
      for plaintext_block in split_blocks(plaintext):
          # CBC mode encrypt: encrypt(plaintext_block XOR previous)
          block = self.encrypt_block(xor_bytes(plaintext_block, previous))
          blocks.append(block)
          previous = block

      return b''.join(blocks)

  def decrypt_cbc(self, ciphertext, iv):
      """
      Decrypts `ciphertext` using CBC mode and PKCS#7 padding, with the given
      initialization vector (iv).
      """
      assert len(iv) == 16

      blocks = []
      previous = iv
      for ciphertext_block in split_blocks(ciphertext):
          # CBC mode decrypt: previous XOR decrypt(ciphertext)
          blocks.append(xor_bytes(previous, self.decrypt_block(ciphertext_block)))
          previous = ciphertext_block

      return unpad(b''.join(blocks))

  def encrypt_pcbc(self, plaintext, iv):
      """
      Encrypts `plaintext` using PCBC mode and PKCS#7 padding, with the given
      initialization vector (iv).
      """
      assert len(iv) == 16

      plaintext = pad(plaintext)

      blocks = []
      prev_ciphertext = iv
      prev_plaintext = bytes(16)
      for plaintext_block in split_blocks(plaintext):
          # PCBC mode encrypt: encrypt(plaintext_block XOR (prev_ciphertext XOR prev_plaintext))
          ciphertext_block = self.encrypt_block(xor_bytes(plaintext_block, xor_bytes(prev_ciphertext, prev_plaintext)))
          blocks.append(ciphertext_block)
          prev_ciphertext = ciphertext_block
          prev_plaintext = plaintext_block

      return b''.join(blocks)

  def decrypt_pcbc(self, ciphertext, iv):
      """
      Decrypts `ciphertext` using PCBC mode and PKCS#7 padding, with the given
      initialization vector (iv).
      """
      assert len(iv) == 16

      blocks = []
      prev_ciphertext = iv
      prev_plaintext = bytes(16)
      for ciphertext_block in split_blocks(ciphertext):
          # PCBC mode decrypt: (prev_plaintext XOR prev_ciphertext) XOR decrypt(ciphertext_block)
          plaintext_block = xor_bytes(xor_bytes(prev_ciphertext, prev_plaintext), self.decrypt_block(ciphertext_block))
          blocks.append(plaintext_block)
          prev_ciphertext = ciphertext_block
          prev_plaintext = plaintext_block

      return unpad(b''.join(blocks))

  def encrypt_cfb(self, plaintext, iv):
      """
      Encrypts `plaintext` with the given initialization vector (iv).
      """
      assert len(iv) == 16

      blocks = []
      prev_ciphertext = iv
      for plaintext_block in split_blocks(plaintext, require_padding=False):
          # CFB mode encrypt: plaintext_block XOR encrypt(prev_ciphertext)
          ciphertext_block = xor_bytes(plaintext_block, self.encrypt_block(prev_ciphertext))
          blocks.append(ciphertext_block)
          prev_ciphertext = ciphertext_block

      return b''.join(blocks)

  def decrypt_cfb(self, ciphertext, iv):
      """
      Decrypts `ciphertext` with the given initialization vector (iv).
      """
      assert len(iv) == 16

      blocks = []
      prev_ciphertext = iv
      for ciphertext_block in split_blocks(ciphertext, require_padding=False):
          # CFB mode decrypt: ciphertext XOR decrypt(prev_ciphertext)
          plaintext_block = xor_bytes(ciphertext_block, self.encrypt_block(prev_ciphertext))
          blocks.append(plaintext_block)
          prev_ciphertext = ciphertext_block

      return b''.join(blocks)

  def encrypt_ofb(self, plaintext, iv):
      """
      Encrypts `plaintext` using OFB mode initialization vector (iv).
      """
      assert len(iv) == 16

      blocks = []
      previous = iv
      for plaintext_block in split_blocks(plaintext, require_padding=False):
          # OFB mode encrypt: plaintext_block XOR encrypt(previous)
          block = self.encrypt_block(previous)
          ciphertext_block = xor_bytes(plaintext_block, block)
          blocks.append(ciphertext_block)
          previous = block

      return b''.join(blocks)

  def decrypt_ofb(self, ciphertext, iv):
      """
      Decrypts `ciphertext` using OFB mode initialization vector (iv).
      """
      assert len(iv) == 16

      blocks = []
      previous = iv
      for ciphertext_block in split_blocks(ciphertext, require_padding=False):
          # OFB mode decrypt: ciphertext XOR encrypt(previous)
          block = self.encrypt_block(previous)
          plaintext_block = xor_bytes(ciphertext_block, block)
          blocks.append(plaintext_block)
          previous = block

      return b''.join(blocks)

  def encrypt_ctr(self, plaintext, iv):
      """
      Encrypts `plaintext` using CTR mode with the given nounce/IV.
      """
      assert len(iv) == 16

      blocks = []
      nonce = iv
      for plaintext_block in split_blocks(plaintext, require_padding=False):
          # CTR mode encrypt: plaintext_block XOR encrypt(nonce)
          block = xor_bytes(plaintext_block, self.encrypt_block(nonce))
          blocks.append(block)
          nonce = inc_bytes(nonce)

      return b''.join(blocks)

  def decrypt_ctr(self, ciphertext, iv):
      """
      Decrypts `ciphertext` using CTR mode with the given nounce/IV.
      """
      assert len(iv) == 16

      blocks = []
      nonce = iv
      for ciphertext_block in split_blocks(ciphertext, require_padding=False):
          # CTR mode decrypt: ciphertext XOR encrypt(nonce)
          block = xor_bytes(ciphertext_block, self.encrypt_block(nonce))
          blocks.append(block)
          nonce = inc_bytes(nonce)

      return b''.join(blocks)


# import os
# from hashlib import pbkdf2_hmac
# from hmac import new as new_hmac, compare_digest

# AES_KEY_SIZE = 16
# HMAC_KEY_SIZE = 16
# IV_SIZE = 16

# SALT_SIZE = 16
# HMAC_SIZE = 32

# def get_key_iv(password, salt, workload=100000):
#   """
#   Stretches the password and extracts an AES key, an HMAC key and an AES
#   initialization vector.
#   """
#   stretched = pbkdf2_hmac('sha256', password, salt, workload, AES_KEY_SIZE + IV_SIZE + HMAC_KEY_SIZE)
#   aes_key, stretched = stretched[:AES_KEY_SIZE], stretched[AES_KEY_SIZE:]
#   hmac_key, stretched = stretched[:HMAC_KEY_SIZE], stretched[HMAC_KEY_SIZE:]
#   iv = stretched[:IV_SIZE]
#   return aes_key, hmac_key, iv


# def encrypt(key, plaintext, workload=100000):
#   """
#   Encrypts `plaintext` with `key` using AES-128, an HMAC to verify integrity,
#   and PBKDF2 to stretch the given key.

#   The exact algorithm is specified in the module docstring.
#   """
#   if isinstance(key, str):
#     key = key.encode('utf-8')
#   if isinstance(plaintext, str):
#     plaintext = plaintext.encode('utf-8')

#   salt = os.urandom(SALT_SIZE)
#   key, hmac_key, iv = get_key_iv(key, salt, workload)
#   ciphertext = AES(key).encrypt_cbc(plaintext, iv)
#   hmac = new_hmac(hmac_key, salt + ciphertext, 'sha256').digest()
#   assert len(hmac) == HMAC_SIZE

#   return hmac + salt + ciphertext


# def decrypt(key, ciphertext, workload=100000):
#   """
#   Decrypts `ciphertext` with `key` using AES-128, an HMAC to verify integrity,
#   and PBKDF2 to stretch the given key.

#   The exact algorithm is specified in the module docstring.
#   """

#   assert len(ciphertext) % 16 == 0, "Ciphertext must be made of full 16-byte blocks."

#   assert len(ciphertext) >= 32, """
#   Ciphertext must be at least 32 bytes long (16 byte salt + 16 byte block). To
#   encrypt or decrypt single blocks use `AES(key).decrypt_block(ciphertext)`.
#   """

#   if isinstance(key, str):
#     key = key.encode('utf-8')

#   hmac, ciphertext = ciphertext[:HMAC_SIZE], ciphertext[HMAC_SIZE:]
#   salt, ciphertext = ciphertext[:SALT_SIZE], ciphertext[SALT_SIZE:]
#   key, hmac_key, iv = get_key_iv(key, salt, workload)

#   expected_hmac = new_hmac(hmac_key, salt + ciphertext, 'sha256').digest()
#   assert compare_digest(hmac, expected_hmac), 'Ciphertext corrupted or tampered.'

#   return AES(key).decrypt_cbc(ciphertext, iv)


# def benchmark():
#   key = b'P' * 16
#   message = b'M' * 16
#   aes = AES(key)
#   for i in range(30000):
#       aes.encrypt_block(message)

# __all__ = ["encrypt", "decrypt", "AES"]

# if __name__ == '__main__':
#   import sys
#   write = lambda b: sys.stdout.buffer.write(b)
#   read = lambda: sys.stdin.buffer.read()

#   if len(sys.argv) < 2:
#       print('Usage: ./aes.py encrypt "key" "message"')
#       print('Running tests...')
#       from tests import *
#       run()
#   elif len(sys.argv) == 2 and sys.argv[1] == 'benchmark':
#       benchmark()
#       exit()
#   elif len(sys.argv) == 3:
#       text = read()
#   elif len(sys.argv) > 3:
#       text = ' '.join(sys.argv[2:])

#   if 'encrypt'.startswith(sys.argv[1]):
#       write(encrypt(sys.argv[2], text))
#   elif 'decrypt'.startswith(sys.argv[1]):
#       write(decrypt(sys.argv[2], text))
#   else:
#       print('Expected command "encrypt" or "decrypt" in first argument.')

#   # encrypt('my secret key', b'0' * 1000000) # 1 MB encrypted in 20 seconds.
