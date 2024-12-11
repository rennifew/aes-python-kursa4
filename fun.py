import os


INPUT_FILE_NAME = ''
ACTION = ''
METHOD = ''


def endless_input(title, *options):

  print(title)
  for i, option in enumerate(options):
    print(f'{i+1}. {option}')
  while True:
    try:
      choice = int(input('Choose an option: ')) - 1
      if (0 <= choice < len(options)):
        return options[choice]
    except ValueError:
      pass
    print('Invalid option. Please try again.')

def choose_file_name(files):
  for i, file_path in enumerate(files):
    print(f'{i+1}. {file_path}')
  while True:
    try:
      choice = int(input('Choose file: ')) - 1
      if (0 <= choice < len(files)):
        return files[choice]
    except ValueError:
      pass
    print('Invalid file. Please try again.')

def choose_encryption_method(aes):
  global METHOD
  
  METHOD = endless_input('Choose method of AES encryption:', 'cbc','pcbc','cfb','ofb','ctr')

  if (METHOD == 'cbc'):
    chosen_encrypt = aes.encrypt_cbc
    chosen_decrypt = aes.decrypt_cbc
  elif (METHOD == 'pcbc'):
    chosen_encrypt = aes.encrypt_pcbc
    chosen_decrypt = aes.decrypt_pcbc
  elif (METHOD == 'cfb'):
    chosen_encrypt = aes.encrypt_cfb
    chosen_decrypt = aes.decrypt_cfb
  elif (METHOD == 'ofb'):
    chosen_encrypt = aes.encrypt_ofb
    chosen_decrypt = aes.decrypt_ofb
  elif (METHOD == 'ctr'):
    chosen_encrypt = aes.encrypt_ctr
    chosen_decrypt = aes.decrypt_ctr
  else:
    raise ValueError('Wrong method')
  return chosen_encrypt, chosen_decrypt


def read_key():
  is_file = endless_input('Use key and salt from files?', 'yes','no')

  if (is_file == 'yes'):
    key_files = os.listdir('./keys/')
    salt_files = os.listdir('./salts/')

    print("Choose key file:")
    key_file = choose_file_name(key_files)
    print("Choose salt file:")
    salt_file = choose_file_name(salt_files)
    
    with open(f'./keys/{key_file}', 'rb') as file:
      key = file.read()
    with open(f'./salts/{salt_file}', 'rb') as file:
      salt = file.read()
  else:
    flag = endless_input('Generate random key and salt?', 'yes', 'no')
    
    key = b''
    if (flag == 'yes'):
      key = os.urandom(16)
      salt = os.urandom(16)
    elif (flag == 'no'):
      key = bytes(input("Enter 16/24/32 chars long KEY to encrypt: ").strip(), 'utf8')
      salt = bytes(input("Enter 16 chars long SALT to encrypt: ").strip(), 'utf8')

    save_key_salt(key, salt)

  print(f'\nKEY: {key}\nSALT: {salt}\n')

  return key, salt


def save_key_salt(key,salt):
  flag = endless_input('Save key and salt?', 'yes', 'no')
  name = input("Enter name for key: ").strip()
  if (flag == 'yes'):
    with open(f'./keys/{name}_key.bin', 'wb') as file:
      file.write(key)
    with open(f'./salts/{name}_salt.bin', 'wb') as file:
      file.write(salt)
  else:
    print('Key and salt not saved.')


def manage_user_input():
  global INPUT_FILE_NAME
  flag = endless_input('What should we encrypt/decrypt?', 'file', 'input')

  if (flag == 'file'):
    INPUT_FILE_NAME = choose_file_name(os.listdir('./input_files/'))
    with open(f'./input_files/{INPUT_FILE_NAME}', 'rb') as file:
      user_input = file.read()
  elif flag == 'input':
    user_input = bytes(input("Enter STRING to encrypt: ").strip(), 'utf8')
  else:
    raise ValueError('Wrong input type')

  return user_input

def manage_output(message):
  global INPUT_FILE_NAME
  global ACTION
  global METHOD
  flag = endless_input("Output should be in:", 'file', 'terminal')

  if (flag == 'terminal'):
    mes = message.decode('utf8') if ACTION == 'decrypt' else message
    print(mes)
  elif (flag == 'file'):
    file_name = INPUT_FILE_NAME.split('.')[0]
    print(f"DEBUG: {INPUT_FILE_NAME}, {file_name}")
    file_ext = 'enc' if ACTION == 'encrypt' else 'dec'
    output_file_path = f'./output_files/{file_name}-{METHOD}.{file_ext}' if file_ext == 'enc' else f'./output_files/{file_name}.{file_ext}'
    with open(output_file_path, 'wb') as file:
      file.write(message)
      print('Output file saved successfully in ' + output_file_path)

def set_action():
  global ACTION
  ACTION = endless_input('Action', 'encrypt', 'decrypt')
