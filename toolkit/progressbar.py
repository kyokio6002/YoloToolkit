import os
import shutil


def show_progress_bar(index, file_path, max_size):
    # progress_bar
    terminal_width = shutil.get_terminal_size().columns
    max_progress_bar_width = 50
    progress_bar_width = min([terminal_width-25, max_progress_bar_width])

    progress_rate = (index+1)//max_size
    progress = progress_rate*progress_bar_width
    progress_bar = '#'*(progress) + ' '*(progress_bar_width-progress_rate)

    file_name = os.path.basename(file_path)
    print("\r", f"[{progress_bar}] ({index+1}/{max_size}){file_name}", end="")
