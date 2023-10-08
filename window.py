"""linker_window - version: 1.0.2-230820

基于 pyqt5 创建的窗口应用, 为用户展示和提供对应账户的个人密码
"""
import os
import sys
import time
import csv
import json

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog  # 继承 QWidget 类
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout  # 设置布局方向
from PyQt5.QtWidgets import QLabel  # 文字标签
from PyQt5.QtWidgets import QLineEdit  # 文本框
from PyQt5.QtWidgets import QMessageBox  # 弹窗提示
from PyQt5.QtWidgets import QPushButton  # 按钮
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem  # 表格

from utils.logger import logger  # 日志


# 定义一个 MainWindow 类，继承自 QWidget 类
class MainWindow(QWidget):
    logger.debug("【初始化】 开始 MainWindow 类初始化")
    logger.info("【信息】打开应用")

    def __init__(self):
        super().__init__()

        # 记录工作状态
        self.is_working = True

        # 设置窗体的标题
        self.setWindowTitle('Linker')
        # 设置窗体的大小
        self.resize(785, 430)
        # 创建总布局 --- 垂直布局
        main_layout = QVBoxLayout()
        # 设置窗口的总布局
        self.setLayout(main_layout)

        # 1.顶部添加表单布局
        main_layout.addLayout(self.init_login_form())
        # 2.添加主功能按钮
        main_layout.addLayout(self.init_main_menu())
        # 3.创建中部表格布局 (table_layout)
        main_layout.addLayout(self.init_table())
        # 4.创建底部菜单布局 (footer_layout)
        main_layout.addLayout(self.init_bottom_menu())

        # 5.线程初始化
        self.init_pwd_producer_thread()

        # 6.加载页面布局
        self.init_load_window_layout()

        # 7.初始化应用工作状态调控器
        self.setWorking(working=False)

        logger.debug("【初始化】 MainWindow 类初始化完成！")

# 1.头部表单
    # 初始化表单
    def init_login_form(self):

        logger.debug("【初始化】 初始化头部表单 ")

        # === 表单全局变量 >
        self.myID_label = QLineEdit()
        self.myID_field = QLineEdit()

        self.key1_label = QLineEdit()
        self.key1_field = QLineEdit()
        self.display1_btn = QPushButton('显示')
        self.add_key2_btn = QPushButton('+')

        self.key2_label = QLineEdit()
        self.key2_field = QLineEdit()
        self.display2_btn = QPushButton('显示')
        self.remove_key2_btn = QPushButton('-')
        self.add_key3_btn = QPushButton('+')

        self.key3_label = QLineEdit()
        self.key3_field = QLineEdit()
        self.display3_btn = QPushButton('显示')
        self.remove_key3_btn = QPushButton('-')
        # ==========================

        # 1.划定 form_layout
        form_layout = QVBoxLayout()

        # 1.1 划定 myID_form_layout
        myID_form_layout = QHBoxLayout()
        form_layout.addLayout(myID_form_layout)

        # 配置 myID_label (ID提示框)
        self.myID_label.setPlaceholderText('名称: ')
        # 设置文本右对齐
        self.myID_label.setAlignment(Qt.AlignRight)
        # 设置输入框背景透明, 无边框
        self.myID_label.setStyleSheet('background-color: transparent; border: none;')
        # 设置初始大小
        self.myID_label.setFixedWidth(60)
        self.myID_label.setFixedHeight(25)

        # 配置 myID_field (ID输入框)
        self.myID_field.setPlaceholderText('为我起个名字吧...')

        # 为了对齐部件使用的伪部件
        replenish_btn = QPushButton('')
        replenish_btn.setFixedWidth(50)
        replenish_btn.setStyleSheet('background-color: transparent; border: none;')

        # 将部件添加至 myID_form_layout
        myID_form_layout.addWidget(self.myID_label)
        myID_form_layout.addWidget(self.myID_field)
        myID_form_layout.addWidget(replenish_btn)
        myID_form_layout.addStretch()

        # 连接事件
        self.myID_label.textChanged.connect(self.align_form)  # 监听文本变化事件
        self.myID_field.textChanged.connect(self.align_form)  # 监听文本变化事件

        logger.debug("【初始化】 已连接表单标签宽度调整事件")

        # 1.2 划定 key1_form_layout
        key1_form_layout = QHBoxLayout()
        form_layout.addLayout(key1_form_layout)

        # 配置 key1_label (密钥1提示框)
        self.key1_label.setPlaceholderText('口令1: ')
        # 设置文本右对齐
        self.key1_label.setAlignment(Qt.AlignRight)
        # 设置输入框背景透明, 无边框
        self.key1_label.setStyleSheet('background-color: transparent; border: none;')
        # 设置初始大小
        self.key1_label.setFixedWidth(60)
        self.key1_label.setFixedHeight(25)

        # 配置 key1_field (密钥1输入框)
        # 设置 key1 文本内容 不可见
        self.key1_field.setEchoMode(QLineEdit.PasswordEchoOnEdit)

        # 设置按钮的宽度
        self.display1_btn.setFixedWidth(40)
        self.add_key2_btn.setFixedWidth(20)

        # 将部件添加至 key1_form_layout
        # key1_form_layout.addStretch()
        key1_form_layout.addWidget(self.key1_label)
        key1_form_layout.addWidget(self.key1_field)
        key1_form_layout.addWidget(self.display1_btn)
        key1_form_layout.addWidget(self.add_key2_btn)
        key1_form_layout.addStretch()

        # 连接事件
        self.display1_btn.clicked.connect(self.toggle_visibility1)
        self.key1_label.textChanged.connect(self.align_form)  # 监听文本变化事件
        self.key1_field.textChanged.connect(self.align_form)  # 监听文本变化事件
        self.add_key2_btn.clicked.connect(self.add_key2)

        logger.debug("【初始化】 已连接 toggle_visibility1 、adjust_width 事件")

        # 1.3 划定 key2_form_layout
        key2_form_layout = QHBoxLayout()
        form_layout.addLayout(key2_form_layout)

        # 配置 key2_label (密钥2提示框)
        self.key2_label.setPlaceholderText('口令2: ')
        # 设置文本右对齐
        self.key2_label.setAlignment(Qt.AlignRight)
        # 设置输入框背景透明, 无边框
        self.key2_label.setStyleSheet('background-color: transparent; border: none;')
        # 设置初始大小
        self.key2_label.setFixedWidth(60)
        self.key2_label.setFixedHeight(25)

        # 配置 key2_field (密钥2输入框)
        # 设置 key2 文本内容 不可见
        self.key2_field.setEchoMode(QLineEdit.PasswordEchoOnEdit)

        # 设置 key2 文本内容可见性按钮的宽度
        self.display2_btn.setFixedWidth(40)
        self.remove_key2_btn.setFixedWidth(20)
        self.add_key3_btn.setFixedWidth(20)

        # 将部件添加至 key2_form_layout
        key2_form_layout.addWidget(self.key2_label)
        key2_form_layout.addWidget(self.key2_field)
        key2_form_layout.addWidget(self.display2_btn)
        key2_form_layout.addWidget(self.remove_key2_btn)
        key2_form_layout.addWidget(self.add_key3_btn)
        key2_form_layout.addStretch()

        # 连接事件
        self.display2_btn.clicked.connect(self.toggle_visibility2)
        self.key2_label.textChanged.connect(self.align_form)  # 监听文本变化事件
        self.key2_field.textChanged.connect(self.align_form)  # 监听文本变化事件
        self.remove_key2_btn.clicked.connect(self.remove_key2)
        self.add_key3_btn.clicked.connect(self.add_key3)

        logger.debug("【初始化】 已连接 toggle_visibility2 、adjust_width 事件")

        # 1.4 划定 key3_form_layout
        key3_form_layout = QHBoxLayout()
        form_layout.addLayout(key3_form_layout)

        # 配置 key3_label (密钥3提示框)
        self.key3_label.setPlaceholderText('口令3: ')
        # 设置文本右对齐
        self.key3_label.setAlignment(Qt.AlignRight)
        # 设置输入框背景透明, 无边框
        self.key3_label.setStyleSheet('background-color: transparent; border: none;')
        # 设置初始大小
        self.key3_label.setFixedWidth(60)
        self.key3_label.setFixedHeight(35)

        # 配置 key3_field (密钥3输入框)
        # 设置 key3 文本内容 不可见
        self.key3_field.setEchoMode(QLineEdit.PasswordEchoOnEdit)

        # 设置 key3 文本内容可见性按钮的宽度
        self.display3_btn.setFixedWidth(40)
        self.remove_key3_btn.setFixedWidth(20)

        # 将部件添加至 key3_form_layout
        key3_form_layout.addWidget(self.key3_label)
        key3_form_layout.addWidget(self.key3_field)
        key3_form_layout.addWidget(self.display3_btn)
        key3_form_layout.addWidget(self.remove_key3_btn)
        key3_form_layout.addStretch()

        # 连接事件
        self.display3_btn.clicked.connect(self.toggle_visibility3)
        self.key3_label.textChanged.connect(self.align_form)  # 监听文本变化事件
        self.key3_field.textChanged.connect(self.align_form)  # 监听文本变化事件
        self.remove_key3_btn.clicked.connect(self.remove_key3)

        logger.debug("【初始化】 已连接 toggle_visibility3 、adjust_width 事件")

        return form_layout

    # add_key2
    def add_key2(self):
        self.key2_label.show()
        self.key2_field.show()
        self.display2_btn.show()
        self.remove_key2_btn.show()
        self.add_key3_btn.show()

        self.add_key2_btn.hide()

    # remove_key2
    def remove_key2(self):
        self.key2_label.hide()
        self.key2_field.hide()
        self.display2_btn.hide()
        self.remove_key2_btn.hide()
        self.add_key3_btn.hide()

        self.add_key2_btn.show()

    # add_key3
    def add_key3(self):
        self.key3_label.show()
        self.key3_field.show()
        self.display3_btn.show()
        self.remove_key3_btn.show()

        self.remove_key2_btn.hide()
        self.add_key3_btn.hide()

    # remove_key3
    def remove_key3(self):
        self.key3_label.hide()
        self.key3_field.hide()
        self.display3_btn.hide()
        self.remove_key3_btn.hide()

        self.remove_key2_btn.show()
        self.add_key3_btn.show()

    # 调整表单组件宽度, 对齐表单
    def align_form(self):

        logger.debug("【事件】 激活调整表单标签宽度")

        # 对齐提示框
        box_id_label_width = self.myID_label.fontMetrics().boundingRect(self.myID_label.text()).width() + 20  # 计算宽度
        key1_label_width = self.key1_label.fontMetrics().boundingRect(self.key1_label.text()).width() + 20
        key2_label_width = self.key2_label.fontMetrics().boundingRect(self.key2_label.text()).width() + 20
        key3_label_width = self.key3_label.fontMetrics().boundingRect(self.key3_label.text()).width() + 20
        label_width = max(box_id_label_width, key1_label_width, key2_label_width, key3_label_width)
        self.myID_label.setFixedWidth(max(label_width, 60))  # 设置最小宽度为 60
        self.key1_label.setFixedWidth(max(label_width, 60))
        self.key2_label.setFixedWidth(max(label_width, 60))
        self.key3_label.setFixedWidth(max(label_width, 60))

        # 对齐输入框
        box_id_field_width = self.myID_field.fontMetrics().boundingRect(self.myID_field.text()).width() + 20  # 计算宽度
        key1_field_width = self.key1_field.fontMetrics().boundingRect(self.key1_field.text()).width() + 20
        key2_field_width = self.key2_field.fontMetrics().boundingRect(self.key2_field.text()).width() + 20
        key3_field_width = self.key3_field.fontMetrics().boundingRect(self.key3_field.text()).width() + 20
        field_width = max(box_id_field_width, key1_field_width, key2_field_width, key3_field_width)
        self.myID_field.setFixedWidth(max(field_width, 150))  # 设置最小宽度为 150
        self.key1_field.setFixedWidth(max(field_width, 150))
        self.key2_field.setFixedWidth(max(field_width, 150))
        self.key3_field.setFixedWidth(max(field_width, 150))

    # 配合按钮,切换 key1 文本框密钥的可见性
    def toggle_visibility1(self):

        logger.debug("【事件】 切换了 key1 文本框的可见性")

        if self.key1_field.echoMode() == QLineEdit.Normal:
            self.key1_field.setEchoMode(QLineEdit.PasswordEchoOnEdit)
            self.display1_btn.setText('显示')
        else:
            self.key1_field.setEchoMode(QLineEdit.Normal)
            self.display1_btn.setText('隐藏')

    # 配合按钮,切换 key2 文本框密钥的可见性
    def toggle_visibility2(self):

        logger.debug("【事件】 切换了 key2 文本框的可见性")

        if self.key2_field.echoMode() == QLineEdit.Normal:
            self.key2_field.setEchoMode(QLineEdit.PasswordEchoOnEdit)
            self.display2_btn.setText('显示')
        else:
            self.key2_field.setEchoMode(QLineEdit.Normal)
            self.display2_btn.setText('隐藏')

    # 配合按钮,切换 key3 文本框密钥的可见性
    def toggle_visibility3(self):

        logger.debug("【事件】 切换了 key3 文本框的可见性")

        if self.key3_field.echoMode() == QLineEdit.Normal:
            self.key3_field.setEchoMode(QLineEdit.PasswordEchoOnEdit)
            self.display3_btn.setText('显示')
        else:
            self.key3_field.setEchoMode(QLineEdit.Normal)
            self.display3_btn.setText('隐藏')

# 2.中部功能区
    # 初始化主功能按钮
    def init_main_menu(self):

        logger.debug("【初始化】初始化主功能按钮")

        # === 按钮全局变量 >
        # 定义全局使用的按钮对象
        self.search_box = QLineEdit()
        self.produce_btn = QPushButton("生成")
        self.export_btn = QPushButton("导出密码")
        self.is_searching = False
        # ==========================

        # 2.1 创建顶部菜单布局 (header_layout)
        header_layout = QHBoxLayout()

        # 2.2.1 配置搜索框
        self.search_box.setPlaceholderText("输入搜索关键字")
        self.search_box.textChanged.connect(self.search_table)
        header_layout.addWidget(self.search_box)

        logger.debug("【初始化】已绑定 search_table 事件 ")

        # 2.2.2 将 produce_btn 按钮添加至布局
        header_layout.addWidget(self.produce_btn)
        # 将"生成"的按钮与生成事件(produce_pwd_event) 绑定
        self.produce_btn.clicked.connect(self.produce_pwd_event)

        logger.debug("【初始化】已绑定 生成 事件 ")

        # 2.2.3 将 export_btn 按钮添加至布局
        header_layout.addWidget(self.export_btn)
        # 将"导出"的按钮与导出密码事件(export_pwd_event) 绑定
        self.export_btn.clicked.connect(self.export_pwd_event)

        logger.debug("【初始化】已绑定 导出 事件 ")

        # 返回顶部菜单布局 (header_layout)对象
        return header_layout

    # 通过关键字筛选表格数据
    def search_table(self, text):

        logger.debug("【事件】激活搜索事件")

        # 设置工作状态
        self.setWorking(searching=True)

        if not text:
            for row in range(self.table_widget.rowCount()):
                self.table_widget.setRowHidden(row, False)
        else:
            for row in range(self.table_widget.rowCount()):
                for col in range(self.table_widget.columnCount()):
                    item = self.table_widget.item(row, col)
                    if item is not None:
                        if text.lower() in item.text().lower():
                            self.table_widget.setRowHidden(row, False)
                            break
                        else:
                            self.table_widget.setRowHidden(row, True)

        # 设置工作状态
        self.setWorking(False, searching=False)

        logger.debug("【事件】搜索事件结束")

    # 密钥为空时提示
    def check_key(self):
        key_text = self.key1_field.text() + self.key2_field.text() + self.key3_field.text()
        if not key_text:
            # setFixedWidth
            label = QLabel('< 注意密钥为空！', self)
            # 位置
            label.move(self.key1_field.x() + 300, self.key1_field.y() - 10)
            # 样式
            label.setStyleSheet("border: 1px solid;background-color: yellow; black")
            # 边框大小
            label_width = label.fontMetrics().boundingRect(label.text()).width() + 20
            label.setFixedWidth(label_width)

            # 显示提示
            label.show()

            # 隐藏提示
            self.key1_field.textChanged.connect(lambda: label.hide())
            self.key2_field.textChanged.connect(lambda: label.hide())
            self.key3_field.textChanged.connect(lambda: label.hide())

# 3.中部表格
    # 创建中间表格的方法
    def init_table(self):

        logger.debug("【初始化】初始化表格")

        # === 表格全局变量 >
        # 定义全局使用的表格对象
        self.table_widget = QTableWidget(0, 7)
        # 将表格水平标题与对应属性连接
        # 条目状态所在行号
        self.state_column = 0
        # 账号信息(明文)所在的行号, 从 0 开始计数
        self.account_info_column = (1, 2, 3)
        # 账户所在的行号
        self.account_column = 1
        # 用户名所在的行号
        self.account_id_column = 2
        # 补充信息所在行号
        self.elucidation_column = 3
        # 长度值所在的行号
        self.length_value_column = 4
        # 密码所在行号
        self.pwd_column = 5
        # 备注所在行号
        self.comments_column = 6
        # 表格添加新行的默认数据 ()
        self.table_default_row_data = [0, '', '', '', 12, '', '']
        # 状态映射
        self.STATE_MAPPING = {
            0: "未启用",
            1: "使用中",
            2: "已过期",
        }
        self.STATE_COLOR_MAPPING = {
            "未启用": r'#E3E6E8',  # 设置为灰色背景
            "使用中": r'#F3FCE6',  # 设置为白色背景
            "已过期": r'#FFB0B0',  # 设置为红色背景
        }
        # ==========================

        # 创建中间表格布局 (table_layout)
        table_layout = QHBoxLayout()
        # 1 将全局表格部件放入表格布局中
        table_layout.addWidget(self.table_widget)

        # 2 设置表头内容和样式
        self.set_horizontal_header()

        # 3 连接相关事件
        # 表格发生变化
        self.table_widget.itemChanged.connect(self.update_table)
        # 单击
        self.table_widget.cellClicked.connect(self.clear_once_pwd)
        # 双击
        self.table_widget.cellDoubleClicked.connect(self.produce_once_pwd)

        logger.debug("【初始化】 已连接 更新表格、clear_once_pwd、produce_once_pwd 事件")

        # 返回 中间表格布局 (table_layout) 对象
        return table_layout

    # 设置表头内容和样式
    def set_horizontal_header(self):
        # 3.1.1 设置横向标题
        table_header = [
            {"field": "status", "text": "状态", 'width': 70},
            {"field": "account", "text": "账户", 'width': 100},
            {"field": "id", "text": "用户名", 'width': 120},
            {"field": "elaborate", "text": "信息补充", 'width': 100},
            {"field": "size", "text": "长度", 'width': 50},
            {"field": "password", "text": "密码", 'width': 162},
            {"field": "comments", "text": "备注", 'width': 100},
        ]
        for idx, info in enumerate(table_header):
            # 设置表格的水平表头的内容
            self.table_widget.setHorizontalHeaderItem(idx, QTableWidgetItem(str(info['text'])))
            # 设置表格的水平表头的宽度
            self.table_widget.setColumnWidth(idx, info['width'])

        logger.debug("【初始化】表头设置完成")

    # 表格更新 (状态列内容映射、更新新行）,
    def update_table(self, item):

        logger.debug("【事件】 表格内容发生变化")

        # === 本应用初始化阶段,对表格进行更新 >
        pass
        # ============================

        # === 不影响表格内容的更新 >
        # 补充填入密码后的颜色映射
        if item.column() == self.pwd_column:
            state_item = self.table_widget.item(item.row(), self.state_column)
            try:
                item_color = QColor(self.STATE_COLOR_MAPPING[state_item.text()])
                item.setBackground(item_color)
                logger.debug("【信息】进行了状态颜色映射")
            except Exception as e:
                logger.warning(f"【错误】生成密码后,进行状态颜色映射发生错误 {e}")
                pass

        # ============================

        if self.is_working:
            return

        # === 本应用初始化后,针对用户操作对表格进行更新 >
        if item.column() == self.state_column:
            # 状态列内容映射
            try:
                state_value = int(item.text())
                if state_value in self.STATE_MAPPING:
                    item.setText(self.STATE_MAPPING[state_value])
                    logger.debug("【信息】 进行了状态列内容映射")
            except Exception:
                item = item
            # 颜色映射
            try:
                state_value = item.text()
                item_color = QColor(self.STATE_COLOR_MAPPING[state_value])
                for col in range(self.table_widget.columnCount()):
                    edit_item = self.table_widget.item(item.row(), col)
                    edit_item.setBackground(item_color)
                logger.debug("【信息】 进行了状态颜色映射")
            except Exception:
                pass

        # 更新新行
        row_count = item.row() + 1
        col = item.column()
        # 如果最后一行的包含用户信息的列被填入内容, 则添加新行
        if row_count == self.table_widget.rowCount() and col in self.account_info_column and item.text():
            self.add_row()

        # ============================

    # 添加新行, 并将默认数据添加到新行, 将列表中的数据添加到表格的最后(list2table_new_row)
    def add_row(self, row=-1, data_list=None):
        """
        向指定行之前添加新行, 并添加指定的数据

        :param row: 从指定行(row)之前添加新行, 默认值为 -1 向最后一行添加新行
        :param data_list: 以列表的形式,指定向新行中添加的数据
        """

        logger.debug("【事件】激活添加新行")

        # self.table_widget.setSortingEnabled(False)  # 添加排序功能

        # 添加行计数器
        add_count = 0

        # 解析 row 参数
        if row == -1:
            current_row_count = self.table_widget.rowCount()  # 获取当前的行数
        elif 0 <= row < self.table_widget.rowCount():
            current_row_count = row
        else:
            return '未知的行数'

        # 解析 data_list 参数
        if data_list is None:
            data_list = self.table_default_row_data
        else:
            data_list = data_list

        self.table_widget.insertRow(current_row_count)  # 在指定行数前添加新行

        # 将列表的数据逐一写入单元格
        for i, cell_data in enumerate(data_list):
            # 尝试映射状态
            try:
                cell_data = self.STATE_MAPPING[int(cell_data)] if i == self.state_column else cell_data
            except ValueError:
                cell_data = cell_data

            # 将数据转换为 setItem 可识别的 QTableWidgetItem 对象
            item_data = QTableWidgetItem(str(cell_data))
            # 注意所有数据已被转换为字符串类型的数据！
            self.table_widget.setItem(current_row_count, i, item_data)  # (行, 列, 数据)
            add_count = add_count + 1

        # 颜色映射
        for row in range(self.table_widget.rowCount()):
            item = self.table_widget.item(row, self.state_column)
            if item.text() in self.STATE_COLOR_MAPPING:
                try:
                    item_color = QColor(self.STATE_COLOR_MAPPING[item.text()])
                    for col in range(self.table_widget.columnCount()):
                        try:
                            item = self.table_widget.item(row, col)
                            item.setBackground(item_color)
                        except Exception:
                            logger.warning(f"【错误】{row},{col} NoneTyp")
                            pass
                except Exception:
                    pass

        # self.table_widget.setSortingEnabled(True)  # 添加排序功能

        logger.debug(f"【信息】已将列表中的数据添加到表格，本次添加次数: {add_count}")

    # 定义快捷键 (用于在表格中删除行和插入行)
    def keyPressEvent(self, event):
        # 使用 Ctrl+D 键 删除指定行
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_D and not self.is_working:
            self.delete_row()

        # 使用 Insert 键 添加新行
        elif event.key() == Qt.Key_Insert and not self.is_working:
            if self.table_widget.rowCount() == 0:
                self.add_row()
            else:
                selected_rows = [index.row() for index in self.table_widget.selectedIndexes()]
                selected_rows.sort(reverse=True)
                for row in selected_rows:
                    self.add_row(row)
        # 使用 Ctrl+E 键 添加新行 (同 Insert 键)
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_E and not self.is_working:
            if self.table_widget.rowCount() == 0:
                self.add_row()
            else:
                selected_rows = [index.row() for index in self.table_widget.selectedIndexes()]
                selected_rows.sort(reverse=True)
                for row in selected_rows:
                    self.add_row(row)

    # 删除选中行(可多选)
    def delete_row(self):
        # 删除表格中选中的行
        selected_rows = [index.row() for index in self.table_widget.selectedIndexes()]
        selected_rows.sort(reverse=True)
        for row in selected_rows:
            self.table_widget.removeRow(row)

            logger.debug("【事件】删除指定行")

# 4. 底部菜单
    # 初始化底部菜单
    def init_bottom_menu(self):

        logger.debug("【初始化】初始化底部菜单")

        # === 底部菜单全局变量 >
        self.save_btn = QPushButton("保存布局")
        self.tip_label = QLabel("Tip")
        # ============================

        # 4. 创建底部菜单布局 (footer_layout)
        bottom_layout = QHBoxLayout()

        # 4.1 将 save_btn 按钮添加到布局
        bottom_layout.addWidget(self.save_btn)

        # 定义保存快捷键
        self.save_btn.setShortcut('ctrl+s')

        # 将"保存布局"的按钮与保存布局的事件(save_layout) 绑定
        self.save_btn.clicked.connect(self.save_layout)

        logger.debug("【初始化】已绑定 保存布局 事件 ")

        # 4.2 定义 查看配置数据 按钮
        view_config_btn = QPushButton("打开数据目录")
        # 将标签添加至布局
        bottom_layout.addWidget(view_config_btn)
        # 将"保存布局"的按钮与保存布局的事件(save_layout) 绑定
        view_config_btn.clicked.connect(self.view_config_event)

        # 4.3 添加弹簧
        bottom_layout.addStretch()

        # 将标签添加至布局
        bottom_layout.addWidget(self.tip_label)

        # 返回 底部菜单布局 (footer_layout) 对象
        return bottom_layout

    # 查看配置数据所在目录
    def view_config_event(self):
        if os.path.exists('db'):
            os.startfile('db')
        else:
            t = time.strftime("%H:%M:%S", time.localtime())
            self.tip_label.setText(f"未找到数据目录 ({t})")

# 5.子线程事件
    # 初始化密码生成器线程事件
    def init_pwd_producer_thread(self):

        logger.debug("【初始化】密码生成器线程")

        # 1. 引入线程, 生成密码
        from utils.PwdToTable_Thread import Pwd2Table
        # 绑定线程对象 - 密码生成器(producer)
        self.producer = Pwd2Table(None, None, None)
        # 将生成密码的线程对象的生命周期设为全局而非函数运行阶段

        # 信号连接
        # 当 producer 完成生成密码的任务会发出 is_done_signal 信号, 并调用 self.show_result() 方法
        self.producer.done_signal.connect(self.pwd2table)

        # 线程错误处理
        self.producer.length_type_error_signal.connect(self.length_type_error_prompt)
        self.producer.length_range_error_signal.connect(self.length_range_error_prompt)
        self.producer.too_many_items_signal.connect(self.too_many_items_error_prompt)

        logger.debug("【初始化】 PwdToTable_Thread 信号连接完成")

    # 提交(start)线程事件1: 生成密码
    def produce_pwd_event(self):

        logger.debug("【事件】激活 生成密码 事件")

        # 设置工作状态
        self.setWorking()

        # 获取箱体名称的内容
        box_id = self.myID_field.text()
        box_id = box_id.strip()  # 头尾去空
        # 空 id 提示
        if not box_id:
            pass
        # 2. 获取密钥的内容
        key = self.key1_field.text().strip() + self.key2_field.text().strip() + self.key3_field.text().strip()

        # 检查密钥是否为空, 空 密钥 提示
        self.check_key()

        # 传递构造密码必要参数
        self.producer.myID = box_id
        self.producer.key = key
        self.producer.table_widget = self.table_widget

        # 生成表格中所有条目的密码
        self.producer.row = -1

        # 提交线程
        self.producer.start()

        logger.debug("【信息】主线已经提交子线程 PwdToTable_Thread ")

    # 提交(start)线程事件2: 生成表格中指定的单条密码
    def produce_once_pwd(self, row, col):
        if col == self.pwd_column:
            logger.debug(f"【事件】触发 单次生成 当前密码（{row}, {col}）事件")

            # 设置工作状态
            self.setWorking()

            # 1. 获取箱体名称的内容
            box_id = self.myID_field.text()
            box_id = box_id.strip()  # 头尾去空

            # 2. 获取密钥的内容
            key = self.key1_field.text().strip() + self.key2_field.text().strip() + self.key3_field.text().strip()

            # 检查密钥是否为空
            self.check_key()

            self.producer.myID = box_id
            self.producer.key = key
            self.producer.table_widget = self.table_widget
            # 生成指定行的密码
            self.producer.row = row
            # 提交线程
            self.producer.start()

            logger.debug("【信息】主线已经提交子线程 PwdToTable_Thread ")

    # 清除表格中指定密码 (非子线程事件, 子线程事件的相关事件)
    def clear_once_pwd(self, row, col):
        if col == self.pwd_column:
            logger.debug(f"【事件】触发 清除当前密码（{row}, {col}） 事件")

            item = QTableWidgetItem('')
            self.table_widget.setItem(row, col, item)
        pass

    # 线程回调主事件: 将生成的密码填入表格 - is_done_signal 信号回调函数
    def pwd2table(self, result_list, row):

        logger.debug("【事件】已接收密码生成器发出的完成信号")

        # 处理多条结果
        if row == -1:
            for r, item_text in enumerate(result_list):
                item = QTableWidgetItem(item_text)
                self.table_widget.setItem(r, self.pwd_column, item)

            # 提示用户
            t = time.strftime("%H:%M:%S", time.localtime())
            self.tip_label.setText(f"密码已生成 ({t})")

            logger.debug("【信息】密码填入完成")

        # 处理单条结果
        elif 0 <= row < self.table_widget.rowCount():
            for result in result_list:
                item = QTableWidgetItem(result)
                self.table_widget.setItem(row, self.pwd_column, item)

                logger.debug("【信息】密码填入完成")

        else:
            logger.debug("【错误】行数指定错误, 密码未正常填入表格")

        # 设置工作状态
        self.setWorking(False)

    # 线程回调事件:用于提示密码长度类型的错误
    def length_type_error_prompt(self, error_count, row, column, tip):

        logger.debug("【事件】已接收密码长度的值类型错误信号")

        # 转化为用户所理解的行列数
        row_count = row + 1
        column_count = column + 1
        if error_count == 1:
            QMessageBox.warning(self, "警告", f"第 {row_count} 行第 {column_count} 列密码长度指定异常\n{tip}")

    # 线程回调事件:用于提示密码长度范围的错误
    def length_range_error_prompt(self, error_count, row, column, tip):

        logger.debug("【事件】已接收密码长度的值范围错误信号")

        # 转化为用户所理解的行列数
        row_count = row + 1
        column_count = column + 1
        if error_count == 1:
            QMessageBox.warning(self, "警告", f"第 {row_count} 行第 {column_count} 列密码长度指定异常\n{tip}")

    # 线程回调事件:用于提示加密项目过多的错误
    def too_many_items_error_prompt(self, num):

        logger.debug("【事件】已接收项目过多的错误信号")

        QMessageBox.warning(self, "警告", f"处理的项目过多,\n一次最多支持处理 {num} 条数据  ")

# 6.数据的加载和导出
    # 加载页面布局和表格数据
    def init_load_window_layout(self):

        logger.debug("【事件】开始加载窗口布局")

        # === 全局变量 >
        # 布局数据文件路径
        self.layout_data_file_path = os.path.join('.', 'db', 'window.json')
        # 表格数据文件路径
        self.table_data_file_path = os.path.join('.', 'db', 'table.csv')
        # ======================

        # 异常处理
        try:
            with open(self.layout_data_file_path, mode='r', encoding='utf-8') as f:
                layout_data = json.load(f)
            # 设置窗口大小
            self.resize(layout_data.get('window_width', self.width()), layout_data.get('window_height', self.height()))

            # 设置表单信息
            self.myID_label.setText(layout_data.get('myID_label', ''))
            self.myID_field.setText(layout_data.get('myID_field', ''))
            self.key1_label.setText(layout_data.get('key1_label', ''))
            self.key2_label.setText(layout_data.get('key2_label', ''))
            self.key3_label.setText(layout_data.get('key3_label', ''))

            # 设置表格行高和列宽
            column_width_list = layout_data.get('column_width_list', [])
            row_height_list = layout_data.get('row_height_list', [])
            for col, width in enumerate(column_width_list):
                self.table_widget.setColumnWidth(col, width)
            for row, height in enumerate(row_height_list):
                self.table_widget.setRowHeight(row, height)

            logger.debug("【信息】成功加载窗口布局")

        # 处理文件缺失
        except FileNotFoundError:
            pass

            logger.warning("【错误】窗口布局数据文件缺失，未能加载")

        # 处理文件编码错误
        except UnicodeDecodeError:
            # 标签提示
            self.tip_label.setText("窗口布局数据文件编码错误!\n请使用 UTF-8 编码的数据文件")
            pass
            # QMessageBox.warning(self, "警告", "窗口布局数据文件编码错误! 请使用 UTF-8 编码的数据文件")

            logger.warning("【错误】窗口布局数据文件编码错误，未能加载")

        # 处理空文件等未知错误
        except Exception:
            pass
            # QMessageBox.warning(self, "警告", "窗口布局数据文件出现未知异常, 未能处理")

            logger.warning("【错误】窗口布局数据文件出现未知异常，未能加载")
        # 调整表单
        finally:
            # 对齐表单
            self.align_form()

            # 清理不使用的密码框
            self.remove_key3()
            self.remove_key2()
            if self.key2_label.text() != '':
                self.add_key2()
                if self.key3_label.text() != '':
                    self.add_key3()

        # 初始化表格数据, 加载数据文件到表格
        self.load_table_data()

    # 加载本地数数据到表格
    def load_table_data(self):

        logger.debug("【事件】开始加载表格数据")

        # 避免文件缺失等错误
        try:
            with open(self.table_data_file_path, mode='r', encoding='utf-8', newline='') as f:
                data = csv.reader(f)
                table_data = [row for row in data]

            logger.debug("【信息】成功加载表格数据")

        # 处理文件缺失
        except FileNotFoundError:
            table_data = [self.table_default_row_data]

            logger.warning("【错误】表格数据文件缺失")

        # 处理文件编码错误
        except UnicodeDecodeError:
            try:
                with open(self.table_data_file_path, mode='r', encoding='GBK', newline='') as f:
                    data = csv.reader(f)
                    table_data = [row for row in data]

                logger.debug("【信息】成功加载表格数据")

            except Exception:
                table_data = [self.table_default_row_data]

                # 标签提示
                self.tip_label.setText("表格数据文件编码错误!\n请使用 UTF-8 编码的数据文件")
                # QMessageBox.warning(self, "警告", "请使用 UTF-8 编码的数据文件")

                logger.warning("【错误】表格数据文件使用了非 UTF-8 / GBK 的编码")

        # 3.2.1.2 将文件中的数据添加到表格
        for row_data in table_data:
            try:
                int(row_data[self.length_value_column])
            except ValueError:
                continue
            if not row_data[self.pwd_column] == '':
                continue
            self.add_row(data_list=row_data)

        # 3.2.3 处理空文件, 并确保表格有一个空行
        if self.table_widget.rowCount() == 0:
            # 如果表格无内容, 直接添加新行
            self.add_row()
        else:
            # 如果表格有内容, 判断最后一行的用户信息是否有内容
            for col in self.account_info_column:
                last_row = self.table_widget.rowCount() - 1
                item = self.table_widget.item(last_row, col)
                if item is not None:
                    if item.text():
                        self.add_row()

                        logger.debug("【信息】已补充空行")

                        break

    # 将窗口布局以及表格中的非密码信息保存到本地
    def save_layout(self):

        # 设置工作状态
        self.setWorking()

        # 获取表格列宽和行高
        column_width_list = [self.table_widget.columnWidth(col) for col in range(self.table_widget.columnCount())]
        row_height_list = [self.table_widget.rowHeight(row) for row in range(self.table_widget.rowCount())]

        # 保存页面布局的项目
        window_layout = {
            'window_width': self.width(),
            'window_height': self.height(),
            'myID_label': self.myID_label.text(),
            'myID_field': self.myID_field.text(),
            'key1_label': self.key1_label.text(),
            'key2_label': self.key2_label.text(),
            'key3_label': self.key3_label.text(),
            'column_width_list': column_width_list,
            'row_height_list': row_height_list,
        }
        # 处理文件夹不存在
        if not os.path.exists('db'):
            os.mkdir('db')
        # 保存页面布局
        with open(self.layout_data_file_path, 'w', encoding='UTF-8') as f:
            json.dump(window_layout, f)

        # 保存表格内容(不包含密码)
        # 处理文件夹不存在
        if not os.path.exists('db'):
            os.mkdir('db')
        # 保存表格内容
        with open(self.table_data_file_path, 'w', encoding='UTF-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["状态", "账户", "用户名", "信息补充", "长度", '密码', "备注"])
            for row in range(self.table_widget.rowCount()):
                row_data = []
                for col in range(self.table_widget.columnCount()):
                    # 跳过密码列
                    if col == self.pwd_column:
                        row_data.append('')
                        continue

                    cell = self.table_widget.item(row, col)
                    if cell is not None:
                        row_data.append(cell.text())
                    else:
                        row_data.append('')
                writer.writerow(row_data)

        # 提示
        t = time.strftime("%H:%M:%S", time.localtime())
        self.tip_label.setText(f"布局保存成功 ({t})")

        logger.info('【信息】保存窗口布局')

        # 设置工作状态
        self.setWorking(False)

    # 导出密码 (适配 keepass)
    def export_pwd_event(self):
        """
        导出密码 (适配 keepass)

        测试表格数据中包含 逗号 和 引号 不影响 csv文件格式,
        测试表格数据中包含 反斜杠 导入 keepass 会识别为空！
        """

        logger.debug("【事件】激活导出密码的事件")

        # 设置工作状态
        self.setWorking()

        # 会弹出一个“保存文件”对话框，让用户选择要保存的文件名和路径。
        file_name, _ = QFileDialog.getSaveFileName(self, "导出CSV文件", "", "CSV Files (*.csv)")
        if file_name:
            with open(file_name, mode='w', newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["Account", "Login Name", "Password", "Web Site", "Comments"])
                for row in range(self.table_widget.rowCount()):
                    row_data = []

                    # 跳过隐藏行
                    if self.table_widget.isRowHidden(row):
                        continue

                    # 过滤 无用户信息的行
                    account_info = ''
                    for col in range(self.table_widget.columnCount()):
                        if col in self.account_info_column:
                            account_info = account_info + self.table_widget.item(row, col).text()
                    if account_info == '':
                        continue

                    # 拷贝数据
                    for col in range(self.table_widget.columnCount()):
                        if col == self.account_column:
                            row_data.append(self.table_widget.item(row, col).text())
                        elif col == self.account_id_column:
                            row_data.append(self.table_widget.item(row, col).text())
                        elif col == self.pwd_column:
                            row_data.append(self.table_widget.item(row, col).text())
                        elif col == self.comments_column:
                            row_data.append('')
                            row_data.append(self.table_widget.item(row, col).text())
                    writer.writerow(row_data)

            t = time.strftime("%H:%M:%S", time.localtime())
            self.tip_label.setText(f"密码已导出 ({t})")

            logger.info("【信息】导出密码")

        # 设置工作状态
        self.setWorking(False)

# 7.大事件调控 - Just one job
    def setWorking(self, working=True, *, searching=False):
        self.is_working = working
        self.is_searching = searching
        if working:
            # 按钮锁, 防连击
            self.produce_btn.setEnabled(False)
            self.export_btn.setEnabled(False)
            self.save_btn.setEnabled(False)

            # 避免影响搜索状态下搜索输入框的可用性
            if not self.is_searching:
                self.search_box.setReadOnly(True)

            logger.debug("【信息】工作中...")

        elif not working:
            # 解除按钮锁_开放按钮功能
            self.produce_btn.setEnabled(True)
            self.export_btn.setEnabled(True)
            self.save_btn.setEnabled(True)

            if not self.is_searching:
                self.search_box.setReadOnly(False)

            logger.debug("【信息】工作结束")


if __name__ == '__main__':
    # 创建一个应用程序对象
    app = QApplication(sys.argv)
    # 创建一个 MainWindow 对象
    window = MainWindow()
    # 显示窗体
    window.show()
    # 进入应用程序的主循环，等待事件的发生
    sys.exit(app.exec_())
