from AES.consts import *

def sub_bytes(s):
  for i in range(4):
    for j in range(4):
      s[i][j] = s_box[s[i][j]]


def inv_sub_bytes(s):
  for i in range(4):
    for j in range(4):
      s[i][j] = inv_s_box[s[i][j]]


def shift_rows(s):
  s[0][1], s[1][1], s[2][1], s[3][1] = s[1][1], s[2][1], s[3][1], s[0][1]
  s[0][2], s[1][2], s[2][2], s[3][2] = s[2][2], s[3][2], s[0][2], s[1][2]
  s[0][3], s[1][3], s[2][3], s[3][3] = s[3][3], s[0][3], s[1][3], s[2][3]


def inv_shift_rows(s):
  s[0][1], s[1][1], s[2][1], s[3][1] = s[3][1], s[0][1], s[1][1], s[2][1]
  s[0][2], s[1][2], s[2][2], s[3][2] = s[2][2], s[3][2], s[0][2], s[1][2]
  s[0][3], s[1][3], s[2][3], s[3][3] = s[1][3], s[2][3], s[3][3], s[0][3]

def add_round_key(s, k):
  for i in range(4):
    for j in range(4):
      s[i][j] ^= k[i][j]


# learned from https://web.archive.org/web/20100626212235/http://cs.ucsb.edu/~koc/cs178/projects/JT/aes.c
xtime = lambda a: (((a << 1) ^ 0x1B) & 0xFF) if (a & 0x80) else (a << 1)


def mix_single_column(a):
  t = a[0] ^ a[1] ^ a[2] ^ a[3]
  u = a[0]
  a[0] ^= t ^ xtime(a[0] ^ a[1])
  a[1] ^= t ^ xtime(a[1] ^ a[2])
  a[2] ^= t ^ xtime(a[2] ^ a[3])
  a[3] ^= t ^ xtime(a[3] ^ u)


def mix_columns(s):
  for i in range(4):
    mix_single_column(s[i])


def inv_mix_columns(s):
  for i in range(4):
    u = xtime(xtime(s[i][0] ^ s[i][2]))
    v = xtime(xtime(s[i][1] ^ s[i][3]))
    s[i][0] ^= u
    s[i][1] ^= v
    s[i][2] ^= u
    s[i][3] ^= v

  mix_columns(s)


def bytes2matrix(text):
  """ Converts a 16-byte array into a 4x4 matrix.  """
  return [list(text[i:i+4]) for i in range(0, len(text), 4)]

def matrix2bytes(matrix):
  """ Converts a 4x4 matrix into a 16-byte array.  """
  return bytes(sum(matrix, []))

def xor_bytes(a, b):
  """ Returns a new byte array with the elements xor'ed. """
  return bytes(i^j for i, j in zip(a, b))

def inc_bytes(a):
  """ Returns a new byte array with the value increment by 1 """
  out = list(a)
  for i in reversed(range(len(out))):
    if out[i] == 0xFF:
      out[i] = 0
    else:
      out[i] += 1
      break
  return bytes(out)

def pad(plaintext):
  """
  Pads the given plaintext with PKCS#7 padding to a multiple of 16 bytes.
  Note that if the plaintext size is a multiple of 16,
  a whole block will be added.
  """
  padding_len = 16 - (len(plaintext) % 16)
  padding = bytes([padding_len] * padding_len)
  return plaintext + padding

def unpad(plaintext):
  """
  Removes a PKCS#7 padding, returning the unpadded text and ensuring the
  padding was correct.
  """
  padding_len = plaintext[-1]
  assert padding_len > 0
  message, padding = plaintext[:-padding_len], plaintext[-padding_len:]
  assert all(p == padding_len for p in padding)
  return message

def split_blocks(message, block_size=16, require_padding=True):
  assert len(message) % block_size == 0 or not require_padding
  return [message[i:i+16] for i in range(0, len(message), block_size)]
