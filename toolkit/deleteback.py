"""
スクリーンショットで[前方,後方]画像が保存される
1.前方画像は名前変更 ex) XXXXXX前方.jpg -> XXXXXX.jpg
2.後方画像は削除
"""
import argparse
import os

# use arg
# parser = argparse.ArgumentParser(description='後方画像を削除し、前方画像の名前変更')
# parser.add_argument('path', help='path')
# args=parser.parse_args()

target_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
target_path = os.path.join(target_path, 'images').replace(os.sep, '/')

print('path:'+target_path)
files = os.listdir(target_path) 

for file in files:
    if "前方" in file:
        print("前方:"+file+"→名前変更します")
        afile = file[:15]+".jpg"
        os.rename(os.path.join(target_path, file), os.path.join(target_path, afile))
    elif "後方" in file:
        print("後方:"+file+"→削除します")
        os.remove(os.path.join(target_path, file))
    else:
        print("error:"+file)