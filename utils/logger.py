"""程序日志记录器"""

import logging
import os


# 设置日志文件路径
log_file_path = os.path.join('.', 'db', 'logger.log')


# 保证本地包含日志文件
def init_log_file():
    if not os.path.exists('db'):
        os.mkdir('db')

    if not os.path.exists(log_file_path):
        with open(log_file_path, mode='w', encoding='utf-8') as f:
            pass


init_log_file()

# 配置日志输出格式
handler = logging.FileHandler(log_file_path, encoding='utf-8')
logging.basicConfig(
    # level=logging.DEBUG,
    level=logging.INFO,
    # level=logging.WARNING,
    # 取消下一行是注释可输出到文件
    handlers=[handler],
    datefmt="%Y-%m-%d %H:%M:%S",
    format="[%(asctime)s %(levelname)s] %(filename)s - %(lineno)d >>> %(message)s"
)

# 创建记录日志的对象 logger
logger = logging.getLogger(__name__)

# 使用 logger 使用示例
logger.debug("已开启调试模式! ")
