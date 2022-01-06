"""
画像をtrimmingする
リサイズだとプレートがつぶれるからtrimmingを行う
中央からやや右下の416*416でtrimmingする
"""
import os
from glob import glob

from PIL import Image, ImageDraw


class Trimming():
    '''trimming'''
    def __init__(self, _import_path, _top_x, _top_y, _width, _height, _ext):
        self.import_path = _import_path
        self.ext = _ext
        self.top_x = _top_x
        self.top_y = _top_y
        self.width = _width
        self.height = _height

    def validation(self):
        images = glob(self.import_path + f"/*.{self.ext}")
        error_flag = False
        for image in images:
            image = Image.open(image)
            _width, _height = image.size
            if self.top_x + self.width > _width:
                error_flag = True
                break
            if self.top_y + self.height > _height:
                error_flag = True
                break
        return error_flag

    def demo_trimming(self):
        test_image = glob(self.import_path + f"/*.{self.ext}")
        if len(test_image) == 0:
            print(f"拡張子が{self.ext}の画像が存在しません")
            return False
        image = Image.open(test_image[0])

        # 領域を囲う
        draw = ImageDraw.Draw(image)
        draw.rectangle((self.top_x, self.top_y, self.top_x+self.width, self.top_y+self.height),
                       outline=(255, 255, 255),
                       width=20)
        image.show()
        result = input("この範囲で全ての画像に対してトリミングを行いますか？(y/n):")
        if result == 'y':
            return True
        return False
        
    def trimming(self, file_path):
        image = Image.open(file_path)
        image_trimming = image.crop((self.top_x,
                                     self.top_y,
                                     self.top_x+self.width,
                                     self.top_y+self.height))
        image_trimming.save(file_path)

    def All_trimming(self):
        images = glob(self.import_path + f"/*.{self.ext}")
        for index, image in enumerate(images):
            # progress_bar
            image_name = os.path.basename(image)
            prog = int(50*(index+1)/len(images))
            progress_bar = '#'*(prog) + ' '*(50-prog)
            print("\r", f"[{progress_bar}] {image_name}", end="")

            self.trimming(image)


if __name__ == "__main__":
    # my setting
    # (left,upper,left,lower)=(852,664,1268,1080)
    ext = input("拡張子を入力してください[jpeg, jpg, JPG, png]:")
    print("切り取りを行う左上の座標(x,y), サイズ(width,height)を入力してください")
    top_x = int(input("x:"))
    top_y = int(input("y:"))
    width = int(input("width:"))
    height = int(input("height:"))
    print("")

    import_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'images').replace(os.sep, '/')
    trimming = Trimming(import_path, top_x, top_y, width, height, ext)
    # valid
    if trimming.validation():
        print("領域が画像範囲がになります")
    else:
        if trimming.demo_trimming():
            trimming.All_trimming()
