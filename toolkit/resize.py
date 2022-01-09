'''resize'''
import os
import shutil
from glob import glob

from PIL import Image

def resize(_import_path, _width, _height, _ext):
    images = glob(_import_path + f'/*.{_ext}')
    if not images:
        print(f"拡張子が{_ext}の画像が存在しません")
        return
    for index, image_path in enumerate(images):
        image = Image.open(image_path)
        image = image.convert('RGB')
        # アスペクト比を保つ
        image.thumbnail([_width, _height])
        # backgroundを白で埋める
        back_ground = Image.new("RGB", (_width, _height), color=(255, 255, 255))
        back_ground.paste(image)
        back_ground.save(image_path)

        # progress_bar
        terminal_width = shutil.get_terminal_size().columns
        bar_count = min([terminal_width-25, 50])
        prog = bar_count*(index+1)//len(images)
        progress_bar = '#'*(prog) + ' '*(bar_count-prog)
        image_name = os.path.basename(image_path)
        print("\r", f"[{progress_bar}] {image_name}", end="")


if __name__ == '__main__':
    import_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'images').replace(os.sep, '/')
    ext = input("拡張子を入力してください[jpeg, jpg, JPG, png]:")
    width = int(input("width:"))
    height = int(input("height:"))
    resize(import_path, width, height, ext)
