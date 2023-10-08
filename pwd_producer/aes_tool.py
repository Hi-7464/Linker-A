"""
基于第三方库 pycryptodomex 实现的 AES 加密工具
加密模式: CBC
填充模式: PKCS7
"""
import base64
import binascii

from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad


# 加密函数, 输出十进制字符串
def encrypt_out_decimal(text, key, iv):
    aes = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))  # 初始化加密器
    encrypted_bytes = aes.encrypt(pad(text.encode('utf-8'), AES.block_size))  # 加密并填充
    decimal_encrypted_text = int.from_bytes(encrypted_bytes, byteorder='big')  # 转换为十进制数
    return str(decimal_encrypted_text)


# 加密函数, 输出十六进制字符串
def encrypt_out_hex(text, key, iv):
    aes = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))  # 初始化加密器
    encrypted_bytes = aes.encrypt(pad(text.encode('utf-8'), AES.block_size))  # 加密并填充
    hex_encrypted_text = binascii.hexlify(encrypted_bytes).decode('utf-8')  # 转换为十六进制字符串
    return hex_encrypted_text


# 加密函数
def encrypt(text, key, iv):
    aes = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))  # 初始化加密器
    encrypted_bytes = aes.encrypt(pad(text.encode('utf-8'), AES.block_size))  # 加密并填充
    base64_encrypted_text = base64.b64encode(encrypted_bytes).decode('utf-8')  # 转换为base64字符串
    return base64_encrypted_text


# 解密函数
def decrypt(text, key, iv):
    aes = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))  # 初始化解密器
    encrypted_bytes = base64.b64decode(text.encode('utf-8'))  # 将base64字符串转换为字节流
    decrypted_bytes = aes.decrypt(encrypted_bytes)  # 解密
    decrypted_text = unpad(decrypted_bytes, AES.block_size).decode('utf-8')  # 去除填充
    return decrypted_text


# 测试
def _test_input_encrypt_decrypt():
    text = input("内容: ")
    key = "3ff34fce19d6b804eff5a3f5747ada4e"
    iv = "a2e8f5d3c1b9e0f7"
    encrypted_text = encrypt(text, key, iv)
    decrypted_text = decrypt(encrypted_text, key, iv)
    print(encrypted_text)
    print(decrypted_text)
    assert decrypted_text == text
    print("成功！")


def _test_encrypt_decrypt_p():
    for i in range(100, 1000):
        text = "1234567887654321123456788765432112345678876543211234567887654321" + str(i)
        key = "3ff34fce19d6b804eff5a3f5747ad" + str(i)
        iv = "a2e8f5d3c1b9e0f7"
        encrypted_text = encrypt(text, key, iv)
        decrypted_text = decrypt(encrypted_text, key, iv)
        print(encrypted_text)
        print(decrypted_text)
        assert decrypted_text == text
        print("成功！", i)


def _test_encrypt_decimal():
    text = "6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b"
    key = "3ff34fce19d6b804eff5a3f5747ada4a"
    iv = "a2e8f5d3c1b9e0f7"
    hex_encrypted_text = encrypt_out_decimal(text, key, iv)
    print(hex_encrypted_text)


if __name__ == '__main__':
    _test_encrypt_decimal()
