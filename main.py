from AES.aes import AES
import fun

if __name__ == '__main__':
  try:
    input = fun.manage_user_input()

    key, salt = fun.read_key()

    aes =  AES(key)

    fun.set_action()

    chosen_encrypt, chosen_decrypt = fun.choose_encryption_method(aes)

    if (fun.ACTION == 'encrypt'):
      message = chosen_encrypt(input, salt)
    else:
      message = chosen_decrypt(input, salt)

    fun.manage_output(message)
    print('Success')
  except Exception as e:
    print(f'Error: {str(e)}')



