"""
スクリーンショットで[前方,後方]画像が保存される
1.前方画像は名前変更 ex) XXXXXX前方.jpg -> XXXXXX.jpg
2.後方画像は削除
"""
import os
# import argparse

# use arg
# parser = argparse.ArgumentParser(description='後方画像を削除し、前方画像の名前変更')
# parser.add_argument('path', help='path')
# args=parser.parse_args()

target_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
target_path = os.path.join(target_path, 'images').replace(os.sep, '/')

print('path:'+target_path)
files = os.listdir(target_path) 

for file in files:
    try:
        if "前方" in file:
            print(f'ファイル名変更: {file}')
            afile = file[:15]+".jpg"
            os.rename(os.path.join(target_path, file), os.path.join(target_path, afile))
        elif "後方" in file:
            print(f'ファイルを削除: {file}')
            os.remove(os.path.join(target_path, file))
        else:
            print("error:"+file)
    except FileExistsError:
        print(f'同名ファイルが存在します: {file}')
