'''xml->txt'''
import os
import pathlib
import random
from glob import glob
from pprint import pprint
from xml.etree import ElementTree

import cv2

from lxml import etree

from progressbar import show_progress_bar


XML_EXT = '.xml'
ENCODE_METHOD = 'utf-8'


class PascalVocReader:
    def __init__(self, filepath):
        # shapes type:
        # [labbel, [(x1,y1), (x2,y2), (x3,y3), (x4,y4)], color, color, difficult]
        self.shapes = []
        self.filepath = filepath
        self.verified = False
        try:
            self.parseXML()
        except:
            pass

    def getShapes(self):
        return self.shapes

    def addShape(self, label, bndbox, filename, difficult):
        xmin = float(bndbox.find('xmin').text)
        ymin = float(bndbox.find('ymin').text)
        xmax = float(bndbox.find('xmax').text)
        ymax = float(bndbox.find('ymax').text)
        points = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]
        self.shapes.append((label, points, filename, difficult))

    def parseXML(self):
        assert self.filepath.endswith(XML_EXT), 'Unsupport file format'
        parser = etree.XMLParser(encoding=ENCODE_METHOD)
        xmltree = ElementTree.parse(self.filepath, parser=parser).getroot()
        path = xmltree.find('path').text
        try:
            verified = xmltree.attrib['verified']
            if verified == 'yes':
                self.verified = True
        except KeyError:
            self.verified = False

        for object_iter in xmltree.findall('object'):
            bndbox = object_iter.find('bndbox')
            label = object_iter.find('name').text

            difficult = False
            if object_iter.find('difficult') is not None:
                difficult = bool(int(object_iter.find('difficult').text))
            self.addShape(label, bndbox, path, difficult)
        return True


class MakeDataset:
    def __init__(self):
        self.classes = {}
        self.class_count = {}
        self.parentpath = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace(os.sep, '/')
        self.ext = '.jpg'  # [.jpg or .png]
        try:
            self.convert()
            self.make_namefile()
            self.make_datafile()
            self.data_split()
        except:
            pass


    def convert(self):
        '''xml->txt'''
        vocFile = glob(os.path.join(self.parentpath, 'VoTT').replace(os.sep, '/') + '/*PascalVOC-export')
        if len(vocFile) > 1:
            print('vocFileが複数存在します')
        else:
            vocFile = vocFile[0].replace(os.sep, '/')

        addxmlpath = os.path.join(vocFile, 'Annotations').replace(os.sep, '/')
        addimgpath = os.path.join(vocFile, 'JPEGImages') .replace(os.sep, '/')
        outputpath = os.path.join(self.parentpath, 'YoloDataset').replace(os.sep, '/')

        xmlPaths = glob(addxmlpath + '/*.xml')

        print('実行中')
        for count, xmlPath in enumerate(xmlPaths):
            tVocParseReader = PascalVocReader(xmlPath)
            shapes = tVocParseReader.getShapes()

            outputFile = os.path.join(outputpath, pathlib.PurePath(xmlPath).stem+'.txt').replace(os.sep, '/')
            filename = os.path.join(addimgpath, pathlib.PurePath(xmlPath).stem+self.ext).replace(os.sep, '/')

            # YoloDatasetにimgを参照元のimgを追加
            img = os.path.join(outputpath, os.path.basename(filename)).replace(os.sep, '/')
            cv2.imwrite(img, cv2.imread(filename))

            show_progress_bar(count, xmlPath, max_size=len(xmlPaths))

            with open(outputFile, 'w', encoding='utf-8') as f:
                for shape in shapes:
                    # shape:[label, bndbox, path, difficult]
                    class_name = shape[0]
                    # shape[1]:[(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]
                    box = shape[1]

                    # クラス(ラベル)を追加していく
                    if class_name not in self.classes:
                        self.classes[class_name] = len(self.classes)
                    class_idx = self.classes[class_name]

                    # classをカウントする
                    if class_name not in self.class_count:
                        self.class_count[class_name] = 1
                    self.class_count[class_name] += 1

                    (height, width, _) = cv2.imread(filename).shape
                    coord_min = box[0]
                    coord_max = box[2]

                    x_center = float((coord_min[0] + coord_max[0])) / 2 / width
                    y_center = float((coord_min[1] + coord_max[1])) / 2 / height
                    w = float((coord_max[0] - coord_min[0])) / width
                    h = float((coord_max[1] - coord_min[1])) / height

                    # 書き込み
                    f.write(f'{class_idx} {x_center:.06f} {y_center:.06f} {w:.06f} {h:.06f}\n')
        print('\n')

    def make_namefile(self):
        '''.nameファイルを作成'''
        classes_name = os.path.join(self.parentpath, 'cfg/classes.name').replace(os.sep, '/')
        pprint(sorted(self.classes.items()))
        pprint(sorted(self.class_count.items()))
        with open(classes_name, 'w', encoding='utf-8') as f:
            for key in self.classes:
                f.write(f'{key}\n')

    def make_datafile(self):
        '''.dataファイルを作成'''

        datafile = os.path.join(self.parentpath, 'cfg/test.data').replace(os.sep, '/')

        # paths
        train_path  = os.path.join(self.parentpath, 'cfg/train.txt').replace(os.sep, '/')
        valid_path  = os.path.join(self.parentpath, 'cfg/valid.txt').replace(os.sep, '/')
        names_path  = os.path.join(self.parentpath, 'cfg/classes.name').replace(os.sep, '/')
        backup_path = os.path.join(self.parentpath, 'backup').replace(os.sep, '/')

        with open(datafile, 'w', encoding='utf-8') as f:
            f.write(f'classes = {len(self.classes)}\n')
            f.write(f'train = {train_path}\n')
            f.write(f'valid = {valid_path}\n')
            f.write(f'names = {names_path}\n')
            f.write(f'backup = {backup_path}\n')

    def data_split(self):
        '''train,valid,testに分割する'''
        # 割合設定
        train_rate = 0.7
        valid_rate = 0.2
        # test_rate = 0.1  # test_rate=1-train_rate-valid_rate

        # 画像取得
        imagepath = os.path.join(self.parentpath, 'YoloDataset').replace(os.sep, '/')
        images = glob(imagepath + f'/*{self.ext}')

        random.seed(100)
        random.shuffle(images)

        # 分割
        train_imgs = images[:int(len(images)*train_rate)]
        valid_imgs = images[int(len(images)*train_rate):int(len(images)*(train_rate+valid_rate))]
        test_imgs  = images[int(len(images)*(train_rate+valid_rate)):]

        # 書き込み
        datas = {'train': train_imgs, 'valid': valid_imgs, 'test': test_imgs}
        for key, value in datas.items():
            txt_path = os.path.join(self.parentpath, f'cfg/{key}.txt').replace(os.sep, '/')
            print(f'{key}:{len(value)}')
            with open(txt_path, 'w', encoding='utf-8') as f:
                for image in value:
                    image = image.replace(os.sep, '/')
                    f.write(image+'\n')


if __name__ == '__main__':
    MakeDataset()
