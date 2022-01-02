'''xml->txt'''
import os
import pathlib
from glob import glob
from xml.etree import ElementTree

import cv2

from lxml import etree


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
        assert self.filepath.endswith(XML_EXT), "Unsupport file format"
        parser = etree.XMLParser(encoding=ENCODE_METHOD)
        xmltree = ElementTree.parse(self.filepath, parser=parser).getroot()
        # filename = xmltree.find('filename').text
        path = xmltree.find('path').text
        try:
            verified = xmltree.attrib['verified']
            if verified == 'yes':
                self.verified = True
        except KeyError:
            self.verified = False

        for object_iter in xmltree.findall('object'):
            bndbox = object_iter.find("bndbox")
            label = object_iter.find('name').text
            # Add chris

            difficult = False
            if object_iter.find('difficult') is not None:
                difficult = bool(int(object_iter.find('difficult').text))
            self.addShape(label, bndbox, path, difficult)
        return True


class MakeDataset:
    def __init__(self):
        self.classes = {}
        self.parentpath = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace(os.sep, '/')
        self.ext = '.jpg'  # [.jpg or .png]

    def convert(self):
        '''xml->txt'''
        # paths/files
        vocFile = glob(os.path.join(self.parentpath, 'VoTT').replace(os.sep, '/') + "/*PascalVOC-export")
        if len(vocFile) > 1:
            print("vocFileが複数存在します")
        else:
            vocFile = vocFile[0].replace(os.sep, '/')
        addxmlpath = os.path.join(vocFile, "Annotations").replace(os.sep, '/')
        addimgpath = os.path.join(vocFile, "JPEGImages") .replace(os.sep, '/')
        outputpath = os.path.join(self.parentpath, "YoloDataset").replace(os.sep, '/')

        xmlPaths = glob(addxmlpath + "/*.xml")

        for count, xmlPath in enumerate(xmlPaths):
            tVocParseReader = PascalVocReader(xmlPath)
            shapes = tVocParseReader.getShapes()

            # 拡張子変換した出力ファイルを設定
            outputFile = os.path.join(outputpath, pathlib.PurePath(xmlPath).stem+".txt").replace(os.sep, '/')
            # imgpath
            filename = os.path.join(addimgpath, pathlib.PurePath(xmlPath).stem+self.ext).replace(os.sep, '/')

            # YoloDatasetにimgを参照元のimgを追加
            img = os.path.join(outputpath, os.path.basename(filename)).replace(os.sep, '/')
            print("{}/{}: {}".format(count+1, len(xmlPaths), os.path.basename(img)))
            cv2.imwrite(img, cv2.imread(filename))

            with open(outputFile, "w") as f:
                for shape in shapes:
                    # shape:[label, bndbox, path, difficult]
                    class_name = shape[0]
                    # shape[1]:[(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]
                    box = shape[1]

                    # クラス(ラベル)を追加していく
                    if class_name not in self.classes:
                        self.classes[class_name] = len(self.classes)
                    class_idx = self.classes[class_name]

                    (height, width, _) = cv2.imread(filename).shape
                    coord_min = box[0]
                    coord_max = box[2]

                    xcen = float((coord_min[0] + coord_max[0])) / 2 / width
                    ycen = float((coord_min[1] + coord_max[1])) / 2 / height
                    w = float((coord_max[0] - coord_min[0])) / width
                    h = float((coord_max[1] - coord_min[1])) / height

                    # 書き込み
                    f.write("%d %.06f %.06f %.06f %.06f\n" % (class_idx, xcen, ycen, w, h))
                    print(class_idx, xcen, ycen, w, h)

    def make_namefile(self):
        '''.nameファイルを作成'''
        classes_name = os.path.join(self.parentpath, "classes.name").replace(os.sep, '/')
        print(self.classes)
        with open(classes_name, "w") as f:
            for key in self.classes:
                # print(key)
                f.write("%s\n" % key)

    def make_datafile(self):
        '''.dataファイルを作成'''
        datafile = os.path.join(self.parentpath, 'cfg/test.data').replace(os.sep, '/')
        # paths
        train_path = os.path.join(self.parentpath, 'cfg/train.txt').replace(os.sep, '/')
        valid_path = os.path.join(self.parentpath, 'cfg/valid.txt').replace(os.sep, '/')
        names_path = os.path.join(self.parentpath, 'classes.name').replace(os.sep, '/')
        backup_path = os.path.join(self.parentpath, 'backup').replace(os.sep, '/')
        with open(datafile, 'w') as f:
            f.write("classes = {}\n".format(len(self.classes)))
            f.write("train = {}\n".format(train_path))
            f.write("valid = {}\n".format(valid_path))
            f.write("names = {}\n".format(names_path))
            f.write("backup = {}\n".format(backup_path))

    def data_split(self):
        '''train,valid,testに分割する'''
        # 割合設定
        train_rate = 0.7
        valid_rate = 0.2
        # test_rate = 0.1  # test_rate=1-train_rate-valid_rate

        # 画像取得
        imagepath = os.path.join(self.parentpath, 'YoloDataset').replace(os.sep, '/')
        images = glob(imagepath + "/*{}".format(self.ext))  # シャッフルしたい

        # 分割
        train_imgs = images[:int(len(images)*train_rate)]
        valid_imgs = images[int(len(images)*train_rate):int(len(images)*(train_rate+valid_rate))]
        test_imgs = images[int(len(images)*(train_rate+valid_rate)):]

        # 書き込み
        datas = {'train': train_imgs, 'valid': valid_imgs, 'test': test_imgs}
        for key, value in datas.items():
            txt_path = os.path.join(self.parentpath, 'cfg/{}.txt'.format(key)).replace(os.sep, '/')
            print(len(value))
            with open(txt_path, 'w') as f:
                for image in value:
                    image = image.replace(os.sep, '/')
                    f.write(image+'\n')

    def make_dataset(self):
        '''各種実行'''
        self.convert()
        self.make_namefile()
        self.make_datafile()
        self.data_split()


if __name__ == "__main__":
    MakeDataset().make_dataset()