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

    def test_trimming(self):
        test_image = glob(self.import_path + f"/*{self.ext}")[0]
        image = Image.open(test_image)

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
        print(f"trimmingを開始します: {file_path}")
        image = Image.open(file_path)
        image_trimming = image.crop((self.top_x,
                                     self.top_y,
                                     self.top_x+self.width,
                                     self.top_y+self.height))
        image_trimming.save(file_path)

    def All_trimming(self):
        files = glob(self.import_path + f"/*{self.ext}")
        for file in files:
            # print(file)
            self.trimming(file)


if __name__ == "__main__":
    # my setting
    # left: 852
    # right: 1268
    # upper: 664
    # upper: 1080
    ext = input("拡張子を入力してください[.jpeg, .jpg,.JPG, .png]:")
    print("切り取りを行う左上の座標(x,y), サイズ(width,height)を入力してください")
    top_x = int(input("x:"))
    top_y = int(input("y:"))
    width = int(input("width:"))
    height = int(input("height:"))
    print("")

    import_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'images').replace(os.sep, '/')
    trimming = Trimming(import_path, top_x, top_y, width, height, ext)
    # valid
    if trimming.test_trimming():
        trimming.All_trimming()
