"""
基于 QThread 创建的窗口子线程, 用于获取主窗口数据并生成对应的密码
"""
from PyQt5.QtCore import QThread, pyqtSignal    # 子线程 和 信号

from pwd_producer.main_aes import get_pwd       # 加载构造密码的算法
from utils.logger import logger     # 日志


class Pwd2Table(QThread):
    logger.debug("【初始化】Pwd2Table 类")

    # 创建信号, pyqtSignal(返回类型)
    done_signal = pyqtSignal(list, int)
    length_type_error_signal = pyqtSignal(int, int, int, str)
    length_range_error_signal = pyqtSignal(int, int, int, str)
    too_many_items_signal = pyqtSignal(int)

    # === 将表格水平标题与对应属性连接 >
    # 账号信息(明文)所在的行, 从 0 开始计数
    account_info_column = (1, 2, 3)
    # 长度值所在的行
    length_column = 4
    # 密码所在行
    pwd_column = 5
    # ================

    def __init__(self, table_widget, myID, key):
        super().__init__()
        logger.debug("【初始化】子线程 Pwd2Table类的对象被初始化 ")
        self.table_widget = table_widget
        self.myID = myID
        self.key = key
        self.row = -1
        self.items_max = 10000

    def run(self):
        logger.debug("【事件】子线程 Pwd2Table 启动")

        # 定义线程返回结果的变量 和 信号的计数器
        result = []
        length_type_error_count = 0
        length_range_error_count = 0
        items_count = 0
        row_data = None

        # 生成表格中所有条目的密码
        if self.row == -1:
            row_data = range(self.table_widget.rowCount())

        # 生成指定行的密码
        if 0 <= self.row < self.table_widget.rowCount():
            row_data = [self.row]

        try:
            # 扫描表格的每行数据
            for row in row_data:
                # 1.定义相关变量
                account_info = ""
                length_value = 0
                pwd = ""

                # 不改变隐藏的行
                if self.table_widget.isRowHidden(row):
                    pwd = self.table_widget.item(row, self.pwd_column).text()
                    result.append(pwd)
                    continue

                # 2.扫描表格的每格单元格数据, 整合账户信息 并 检查参数
                for column in range(self.table_widget.columnCount()):
                    # 整合账户信息
                    if column in self.account_info_column:
                        account_info = account_info + self.table_widget.item(row, column).text().strip()
                    # 整合账户信息不存在时跳过生成密码的步骤
                    if not account_info:
                        continue

                    if column == self.length_column:
                        length_value = self.table_widget.item(row, column).text()

                # 3.计数 与 规模限制
                items_count = items_count + 1
                # 超过最大处理条数的处理方法
                if items_count > self.items_max:
                    self.too_many_items_signal.emit(self.items_max)
                    # 仅处理前 (self.max_number_items) 条数据
                    break

                logger.debug(f"【信息】子线程 Pwd2Table 处理了 {items_count} 条信息")

                # 4.异常处理 和 获取密码
                if (not account_info) or length_value == 0 or length_value == '0':
                    pwd = ""
                else:
                    try:
                        text = account_info + str(length_value)
                        pwd = get_pwd(text, self.myID, self.key, length_value)

                    # 处理 length_value 类型错误
                    except TypeError as tip:
                        pwd = ""
                        length_type_error_count = length_type_error_count + 1
                        self.length_type_error_signal.emit(length_type_error_count, row, self.length_column, str(tip))
                    # 处理 length_value 值(范围)错误
                    except ValueError as tip:
                        pwd = ""
                        length_range_error_count = length_range_error_count + 1
                        self.length_range_error_signal.emit(length_range_error_count, row, self.length_column, str(tip))

                # 5. 将密码添加至结果列表
                result.append(pwd)
        except Exception:
            logger.warning("【错误】可能是变量 self.row 指定错误 ")

        # 返回结果
        self.done_signal.emit(result, self.row)

        logger.debug("密码生成器线程结束运行")
