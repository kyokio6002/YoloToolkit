"""
画像をtrimmingする
リサイズだとプレートがつぶれるからtrimmingを行う
中央からやや右下の416*416でtrimmingする
"""
from PIL import Image
from glob import glob

class Trimming():
    def __init__(self, left, upper, right, lower):
        self.import_path = input("入力ファイルのフォルダパスを入力してください: ")
        self.left = left
        self.right = right
        self.upper = upper
        self.lower = lower

    def trimming(self, file_path):
        print("trimmingを開始します: {}".format(file_path))
        image = Image.open(file_path)
        # print("画像を開きました")
        image_trimming = image.crop((self.left, self.upper, self.right, self.lower))
        image_trimming.save(file_path)
        # print("保存が完了しました")

    def All_trimming(self):
        files = glob(self.import_path + "/*.jpg")
        for file in files:
            # print(file)
            self.trimming(file)
        

if __name__ == "__main__":
    centerX = 960
    centerY = 540
    biasX = 100
    biasY = 332

    left = centerX-208+biasX
    right = centerX+208+biasX
    upper = centerY-208+biasY
    lower = centerY+208+biasY

    print("left: {}".format(centerX-208+biasX))
    print("right: {}".format(centerX+208+biasX))
    print("upper: {}".format(centerY-208+biasY))
    print("upper: {}".format(centerY+208+biasY))

    Trimming(left,upper,right,lower).All_trimming()