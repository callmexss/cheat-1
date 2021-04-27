from cheat.colorize import Colorize
from cheat.utils import Utils
import io
import os
from collections import deque


class Sheets:

    def __init__(self, config):
        self._config = config
        self._colorize = Colorize(config)

        # Assembles a dictionary of cheatsheets as name => file-path
        self._sheets = {}
        sheet_paths = [
            config.cheat_user_dir
        ]

        # merge the CHEAT_PATH paths into the sheet_paths
        if config.cheat_path:
            for path in config.cheat_path.split(os.pathsep):
                if os.path.isdir(path):
                    sheet_paths.append(path)

        if not sheet_paths:
            Utils.die('The CHEAT_USER_DIR dir does not exist '
                      + 'or the CHEAT_PATH is not set.')

        # otherwise, scan the filesystem
        for cheat_dir in reversed(sheet_paths):
            self._sheets.update(
                dict([
                    (cheat, os.path.join(cheat_dir, cheat))
                    for cheat in os.listdir(cheat_dir)
                    if not cheat.startswith('.')
                    and not cheat.startswith('__')
                ])
            )

    def directories(self):
        """ Assembles a list of directories containing cheatsheets """
        sheet_paths = [
            self._config.cheat_user_dir,
        ]

        # merge the CHEATPATH paths into the sheet_paths
        for path in self._config.cheat_path.split(os.pathsep):
            sheet_paths.append(path)

        return sheet_paths

    def get(self):
        """ Returns a dictionary of cheatsheets as name => file-path """
        return self._sheets

    def list(self):
        """ Lists the available cheatsheets """
        sheet_list = ''
        pad_length = max([len(x) for x in self.get().keys()]) + 4
        for sheet in sorted(self.get().items()):
            sheet_list += sheet[0].ljust(pad_length) + sheet[1] + "\n"
        return sheet_list

    def search(self, term):
        """ Searches all cheatsheets for the specified term """
        result = ''

        for cheatsheet in sorted(self.get().items()):
            match = ''
            for line in io.open(cheatsheet[1], encoding='utf-8'):
                if term in line:
                    match += '  ' + self._colorize.search(term, line)

            if match != '':
                result += cheatsheet[0] + ":\n" + match + "\n"

        return result

    def _parse_one(self, cheatsheet, term):
        index = 0
        tmp_li = []
        contents_list = io.open(cheatsheet[1], encoding='utf-8').readlines()
        length = len(contents_list)

        while index < length:
            line = contents_list[index]
            if term not in line:
                index += 1
                continue
            else:
                # find the first empty line or up or bottom of the file from this line
                left_index = index - 1
                right_index = index + 1
                tmp_q = deque([line])
                left_hit = False
                right_hit = False

                while not left_hit or not right_hit:
                    if not left_hit and left_index >= 0 and contents_list[left_index].strip():
                        tmp_q.appendleft(contents_list[left_index])
                        left_index -= 1
                    else:
                        left_hit = True

                    if not right_hit and right_index < length and contents_list[right_index].strip():
                        tmp_q.append(contents_list[right_index])
                        right_index += 1
                    else:
                        index = right_index
                        right_hit = True

                tmp_li.append(''.join(tmp_q))

        return '\n'.join(tmp_li)

    def upgrade_search(self, term):
        """ Searches all cheatsheets for the specified term """
        ret = []

        for cheatsheet in sorted(self.get().items()):
            sheet_result = ''.join(self._parse_one(cheatsheet, term))
            if sheet_result:
                ret.append(cheatsheet[0] + ":\n" + sheet_result)
       
        return '\n'.join(ret) + '\n' if ret else ''
