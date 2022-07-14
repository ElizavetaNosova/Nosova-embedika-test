import os
from copy import copy


class MenuPageLinkManager:
    _separator = '\n'
    def __init__(self, link_template, log_dir = './logs',
                 first_page_idx=0, restart=False):
        progress_tracking_file_dir = os.path.abspath(log_dir)
        os.makedirs(progress_tracking_file_dir, exist_ok=True)
        self.log_file_path = os.path.join(progress_tracking_file_dir, 'menu_mage_progress_log.txt')

        self._default_page_idx = first_page_idx-1
        self.__current_page_idx = self._default_page_idx if restart or not os.path.exists(self.log_file_path) else self.get_last_logged_idx()
        self.link_template = link_template

    def get_next_page_link(self):
       self.log()
       self.__current_page_idx+=1
       return self.get_current_page_link()

    def get_current_page_link(self):
       return self.link_template.format(self.__current_page_idx)

    def log(self):
        with open(self.log_file_path, 'a') as f:
           f.write(f'{self._separator}{self.__current_page_idx}')

    def get_last_logged_idx(self):
        try:
            with open(self.log_file_path) as f:
                last_log = int(f.read().strip().split(self._separator)[-1])
                # если стартовая страница была исправлена на большее значение, используем его, а не лог
                return max(last_log, self._default_page_idx)
        # файл может не существовать или содержать некорректные данные, которые невозможно преобразовать в число
        except FileNotFoundError:
            return self._default_page_idx
        except ValueError:
            return self._default_page_idx

    def get_idx(self):
        return copy(self.__current_page_idx)
