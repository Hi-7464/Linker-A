import re

from pwd_producer.aes_tool import encrypt_out_decimal
from utils.logger import logger  # 日志

pwd_min_len = 3
pwd_max_len = 45


# length要大于 3, 小于 45
# 经过9万条数据测试, 64位字符串经过 encrypt_out_decimal 结果最小为 189 位数字
# 189 / 4 = 47.25, 留部分余量取45
# 估算结果小于 45 的概率约为万亿分之一


def get_pwd(text, ID, KEY, length):
    """
    一种结合对称加密，以及散列算法，便捷构造个人密码的方法。

    用户通过指定特定的的 KEY 和 ID（对应对称加密算法的 密钥 和 IV），
    对不同明文(账户信息)进行对称加密，再对加密结果进行特定的字符编码，
    进而构造出与账户信息相关联的密码

    :param text: 明文
    :param ID: 自定义的个人 ID
    :param KEY: 密钥
    :param length: 密码长度, 数值的有效范围为 3 ~ 45
    :return: 指定长度的强密码
    """
    logger.debug("【事件】构造密码中...")

    pwd = ""

    # 明文处理
    text = get_sha256(text)
    # 密钥处理
    KEY = get_sha256(KEY, length=32)
    # 身份信息 做 iv 处理
    ID = get_md5(ID, length=16)

    # 长度值类型检查
    try:
        length = int(length)
    except ValueError:
        raise TypeError("密码长度必须是整数")

    # 长度值范围检查
    if length < pwd_min_len or length > pwd_max_len:
        raise ValueError(f"密码长度必须在 {pwd_min_len} 到 {pwd_max_len} 之间")

    # 通过 对称加密 获取特定长度的加密结果（十进制）
    digital_code = encrypt_out_decimal(text, KEY, ID)
    digital_code_required_length = int(length) * 4
    digital_code = digital_code[0:digital_code_required_length]
    # 上述字符截取超出索引范围不报错，会取全部字符

    # 加密结果（十进制） 拆分为 4 位一组的列表
    digital_code_list = split_number_to_list(digital_code)

    # 字符编码
    for cell in digital_code_list:
        pwd_cell = number_string_encoding(cell)
        pwd = pwd + pwd_cell

    # 保证生成强密码（字符种类大于 3）
    if not is_strong_cipher(pwd):
        pwd = pwd[:-3]
        pwd = mending(pwd, digital_code[-6:])

    # 密码长度不达标
    if len(pwd) < length:
        raise ValueError(f"本条结果长度为 {len(pwd)} ,不满足要求, 请是调整长度值")

    return pwd


# 获取一个字符串的 md5 值
def get_md5(str1='', start=0, *, length=32):
    from hashlib import md5
    text = str(str1)
    md5 = md5()
    md5.update(text.encode())
    result = md5.hexdigest()
    result = result[start:(start + length)]
    return result


# 获取一个字符串的 sha256 值
def get_sha256(str1='', start=0, *, length=64):
    from hashlib import sha256
    text = str(str1)
    sha256 = sha256()
    sha256.update(text.encode())
    result = sha256.hexdigest()
    result = result[start:(start + length)]
    return result


# 数字拆分器
def split_number_to_list(num, unit_length=4):
    """
    将任意长度的数字或数字字符串拆分为指定位数(unit_length)一组的列表，并自动在末尾用 ‘0’ 补齐
    :param num: 接收数字或数字字符串
    :param unit_length: 指定每一组数字的位数
    :return: 返回指定位数一组的数字字符串列表
    """
    num_str = str(num)
    num_len = len(num_str)
    remainder = num_len % unit_length
    if remainder != 0:
        num_str = num_str + '0' * (unit_length - remainder)
        num_len += unit_length - remainder
        # print("》split_number()有过补齐操作《")
    num_list = [num_str[i:i + unit_length] for i in range(0, num_len, unit_length)]
    return num_list


# 编码器
def number_string_encoding(num_str):
    """ 将一个四位数字的字符串映射为一个 ASCII 可见字符的方法

    :param num_str: 接收长度为 4 的由数字构成的字符串, 用于决定返回的字符
    :return: 返回 ASCII 码中 94 个可见字符中特定的一个字符
    """
    # 为了提高兼容性剔除以下 8 个特殊字符: $()-'"`\
    ascii_special_char = ('!', '#', '%', '&', '*', '+',
                          ',', '.', '/', ':', ';', '<',
                          '=', '>', '?', '@', '[', ']',
                          '^', '_', '{', '|', '}', '~')
    ascii_numeric_char = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')
    ascii_capital_letter = ('A', 'B', 'C', 'D', 'E', 'F', 'G',
                            'H', 'I', 'J', 'K', 'L', 'M', 'N',
                            'O', 'P', 'Q', 'R', 'S', 'T', 'U',
                            'V', 'W', 'X', 'Y', 'Z')
    ascii_small_letter = ('a', 'b', 'c', 'd', 'e', 'f', 'g',
                          'h', 'i', 'j', 'k', 'l', 'm', 'n',
                          'o', 'p', 'q', 'r', 's', 't', 'u',
                          'v', 'w', 'x', 'y', 'z')
    ascii_visible_char = (ascii_special_char, ascii_numeric_char, ascii_capital_letter, ascii_small_letter)

    # 参数合规性检查
    if not (isinstance(num_str, str) and num_str.isdigit() and len(num_str) == 4):
        raise ValueError("Only accept strings consisting of 4 digits in length!")

    # 用参数确定字符类型, 参数 character_type_parameters 的范围 [0,3]
    group_of_character_tuple = ascii_visible_char
    character_type_parameter = int(num_str[:2]) * len(group_of_character_tuple) // 100
    specify_character_type = {
        0: ascii_special_char,
        1: ascii_numeric_char,
        2: ascii_capital_letter,
        3: ascii_small_letter
    }.get(character_type_parameter, None)
    if specify_character_type is None:
        raise ValueError("Invalid character type parameter!")

    # 用参数确定字符类型下具体字符
    character_parameter = int(num_str) % len(specify_character_type)
    return specify_character_type[character_parameter]


# 检查器
def is_strong_cipher(pwd_str):
    """
    检查字符种类。如果输入的字符串中包含
    “数字”、“大写字母”、“小写字母”、“特殊字符”中的
    三种及以上返回 True，否则返回 False。

    :param pwd_str: 接收包含 ASCII 可见字符的任意长度的字符串
    :return: 返回 True 或 False
    测试中输入字符包含汉字不会当作特殊字符，不识别，不计数
    """
    count = 0
    if re.search(r'\d', pwd_str):
        count += 1
        # print("有数字")
    if re.search(r'[A-Z]', pwd_str):
        count += 1
        # print("有大写字母")
    if re.search(r'[a-z]', pwd_str):
        count += 1
        # print("有小写字母")
    if re.search(r'[^\w\s]', pwd_str):
        count += 1
        # print("有特殊字符")
    return count >= 3


# 备用机构
def mending(pwd_str, digital_code):
    digital_code = '00' + digital_code[0:2] + '25' + digital_code[2:4] + '50' + digital_code[4:6]
    digital_code_list = split_number_to_list(digital_code)
    for cell in digital_code_list:
        pwd_cell = number_string_encoding(cell)
        pwd_str = pwd_str + pwd_cell

    return pwd_str


if __name__ == '__main__':
    pass
