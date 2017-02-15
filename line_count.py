#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path, listdir
from clint.arguments import Args
from clint.textui import puts, colored, indent

"""
    create a generator get each file under dir
"""


def get_file_path(dir_path, ext):
    abs_path = path.abspath(dir_path)
    file_list = listdir(dir_path)
    for each_node in file_list:
        node_path = abs_path+path.sep+each_node
        if path.isfile(node_path):
            if ext == '' or node_path.endswith(ext):
                yield node_path
        else:
            for each_node_path in get_file_path(node_path, ext):
                yield each_node_path


"""
    count lines in a file
"""


def line_count(file_path, with_comment=False, with_empty_line=False, ext='.php'):
    with open(file_path) as f:
        file_string = f.readlines()
        # filter whitespace in lines of string
        file_string = map(lambda y: y.strip(), file_string)
        # if the result do not contain the number of empty lines
        if not with_empty_line:
            file_string = [x for x in file_string if x != '']
        # if the result do not contain the number of comment lines
        if not with_comment:
            # filter the comment in the form of single line
            file_string = [x for x in file_string if not is_single_line_comment(x, ext)]
            for each_pair in get_multiple_comment_sign_pair(ext):
                if each_pair[0] == each_pair[1]:
                    file_string = pair_replace_symmetry(each_pair[0], file_string)
                else:
                    file_string = pair_replace_asymmetry(each_pair, file_string)
            return len(file_string) - count_lines_multiple_comment(file_string)
        return len(file_string)


"""
    judge a single line is a comment or not
"""


def is_single_line_comment(line, ext='.php'):
    if ext == '.php':
        if line.startswith('#') or line.startswith('//') or (line.startswith('/*') and line.startswith('*/')):
            return True
        return False
    elif ext == '.py':
        if line.startswith('#') \
                or (line.startswith('"""') and line.endswith('"""') and line.find('"""') != line.rfind('"""'))\
                or (line.startswith("'''") and line.endswith("'''") and line.find("'''") != line.rfind("'''")):
            return True
        return False
    elif ext == '.js':
        if line.startswith('//') or (line.startswith('/*') and line.endswith('*/')):
            return True
        return False
    return False


def count_lines_multiple_comment(file_string):
    pair = ('/*', '*/')
    checker = False
    counter = 0
    # count the line without multiple line comments
    for each_string in file_string:
        start_index = each_string.strip().find(pair[0])
        end_index = each_string.strip().find(pair[1])
        if start_index != -1:
            checker = True
            if start_index != 0:
                counter += 1
        if not checker:
            counter += 1
        if end_index != -1:
            checker = False
            if each_string.split(pair[1])[1] != '':
                counter += 1
    return len(file_string) - counter


def pair_replace_symmetry(half_pair, file_string):
    now_num = 0
    index = 0
    for each_string in file_string:
        if each_string.find(half_pair) != -1:
            now_num += 1
        if now_num % 2 == 1:
            each_string = each_string.replace(half_pair, "/*")
        else:
            each_string = each_string.replace(half_pair, "*/")
        file_string[index] = each_string
        index += 1
    return file_string


def pair_replace_asymmetry(pair, file_string):
    if pair == ("/*", "*/"):
        return file_string
    index = 0
    for each_string in file_string:
        if each_string.find(pair[0]) != -1:
            each_string = each_string.replace(pair[0], "/*")
        if each_string.find(pair[1]) != -1:
            each_string = each_string.replace(pair[1], "*/")
        file_string[index] = each_string
        index += 1
    return file_string

"""
    get comment sign with extension name of file
"""


def get_multiple_comment_sign_pair(ext):
    if ext == '.php':
        return [('/*', '*/')]
    elif ext == '.py':
        return [('"""', '"""'), ("'''", "'''")]
    else:
        return [('/*', '*/')]

"""
    count lines in a dir
"""


def line_count_in_dir(dir_path='.', ext='.php', with_comment=True, with_empty_line=False):
    if not path.isdir(dir_path):
        raise Exception("文件夹路径不对")
    count = 0
    for each_file in get_file_path(dir_path, ext):
        count += line_count(each_file, with_comment, with_empty_line, ext)
    return count


"""
    count lines in a file
"""


def line_count_in_file(file_path, ext='.php', with_comment=True, with_empty_line=False):
    if path.isfile(file_path):
        return line_count(file_path, with_comment, with_empty_line, ext)
    else:
        raise Exception("文件路径不对")


def line_count_in_path(node_path, ext='.php', with_comment=True, with_empty_line=False):
    if path.isfile(node_path):
        return line_count(node_path, with_comment, with_empty_line, ext)
    elif path.isdir(node_path):
        return line_count_in_dir(node_path, ext, with_comment, with_empty_line)
    else:
        raise Exception("错误的文件路径")


if __name__ == '__main__':
    all_args = Args().grouped

    for item in all_args:
        if item == '-p' or item == '--path':
            all_path = all_args[item].all
        elif item == '-e' or item == '--ext':
            all_ext = all_args[item].all

    try:
        all_path
    except NameError as e:
        all_path = ['.']
    try:
        all_ext
    except NameError as e:
        all_ext = ['.php']

    total_total_lines = 0
    for each_path in all_path:
        total_lines = 0
        for each_ext in all_ext:
            line_num = line_count_in_path(each_path, each_ext)
            puts("in "+each_path+" there are "
                 + str(line_num)
                 + ' lines code in files with '+each_ext+" extension name")
            total_lines += line_num
        puts("there are "+str(total_lines)+" lines of code in "+each_path)
        total_total_lines += total_lines
    puts("there are "+str(total_total_lines)+" lines of code in this count")


