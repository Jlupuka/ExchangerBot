import logging
from datetime import datetime


# Создаем класс-наследник для изменения поведения logging.Formatter
class ColoredFormatter(logging.Formatter):
    # Словарь с цветами для разных уровней логирования
    COLOR_CODES = {
        'DEBUG': '\33[1;34m',  # ярко-синий
        'INFO': '\33[1;32m',  # ярко-зеленый
        'WARNING': '\33[1;33m',  # ярко-желтый
        'ERROR': '\33[1;31m',  # ярко-красный
        'CRITICAL': '\33[1;41m'  # ярко-красный на белом фоне
    }

    def format(self, record):
        # Получаем форматированное сообщение с помощью родительского класса
        message = super().format(record)
        # Получаем цвет для текущего уровня логирования
        color = self.COLOR_CODES.get(record.levelname)
        time = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        # Возвращаем цветное сообщение
        return f'\33[1;97m{time}  \33[1;95m |' \
               f'  {color}#{record.levelname:<8}\033[0m \33[1;95m |' \
               f'  \33[96m{record.filename}:{record.funcName}\33[92m:\33[1;91m{record.lineno}\033[0m \33[1;95m |' \
               f'\33[0;36m - \33[1;93m{record.name:<2} \33[0;36m-\33[1;95m |  {color}{message}\033[0m'


# Конфигурируем logging
formatter = ColoredFormatter()

handler = logging.StreamHandler()
handler.setFormatter(formatter)

reader_handler = logging.FileHandler(".log", mode='w')
reader_formatter = logging.Formatter("%(asctime)s  | #%(levelname)s |"
                                     " %(filename)s:%(funcName)s:%(lineno)s | - %(name)s - | %(message)s")
reader_handler.setFormatter(reader_formatter)

logger = logging.getLogger()

logger.addHandler(handler)
logger.addHandler(reader_handler)

logger.setLevel(logging.DEBUG)
