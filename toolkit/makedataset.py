'''xml->txt'''
import os
import pathlib
import random
import shutil
from glob import glob
from pprint import pprint
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
        self.class_count = {}
        self.parentpath = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace(os.sep, '/')
        self.ext = '.jpg'  # [.jpg or .png]

    def convert(self):
        '''xml->txt'''
        # paths/files
        vocFile = glob(os.path.join(self.parentpath, 'VoTT').replace(os.sep, '/') + "/*PascalVOC-export")
        if len(vocFile) > 1:
            print("vocFile????????????????????????")
        else:
            vocFile = vocFile[0].replace(os.sep, '/')
        addxmlpath = os.path.join(vocFile, "Annotations").replace(os.sep, '/')
        addimgpath = os.path.join(vocFile, "JPEGImages") .replace(os.sep, '/')
        outputpath = os.path.join(self.parentpath, "YoloDataset").replace(os.sep, '/')

        xmlPaths = glob(addxmlpath + "/*.xml")

        print('?????????')
        for count, xmlPath in enumerate(xmlPaths):
            tVocParseReader = PascalVocReader(xmlPath)
            shapes = tVocParseReader.getShapes()

            # ????????????????????????????????????????????????
            outputFile = os.path.join(outputpath, pathlib.PurePath(xmlPath).stem+".txt").replace(os.sep, '/')
            # imgpath
            filename = os.path.join(addimgpath, pathlib.PurePath(xmlPath).stem+self.ext).replace(os.sep, '/')

            # YoloDataset???img???????????????img?????????
            img = os.path.join(outputpath, os.path.basename(filename)).replace(os.sep, '/')
            cv2.imwrite(img, cv2.imread(filename))

            # ???????????????
            # (1) ??????????????????
            # print("{}/{}: {}".format(count+1, len(xmlPaths), os.path.basename(img)))
            # (2)progress_bar
            terminal_width = shutil.get_terminal_size().columns
            bar_count = min([terminal_width-25, 50])
            xml_name = os.path.basename(xmlPath)
            prog = bar_count*(count+1)//len(xmlPaths)
            progress_bar = '#'*(prog) + ' '*(bar_count-prog)
            print('\r', f'[{progress_bar}] {xml_name}({count+1}/{len(xmlPaths)})', end='')

            with open(outputFile, "w") as f:
                for shape in shapes:
                    # shape:[label, bndbox, path, difficult]
                    class_name = shape[0]
                    # shape[1]:[(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]
                    box = shape[1]

                    # ?????????(?????????)?????????????????????
                    if class_name not in self.classes:
                        self.classes[class_name] = len(self.classes)
                    class_idx = self.classes[class_name]

                    # class?????????????????????
                    if class_name not in self.class_count:
                        self.class_count[class_name] = 1
                    self.class_count[class_name] += 1

                    (height, width, _) = cv2.imread(filename).shape
                    coord_min = box[0]
                    coord_max = box[2]

                    xcen = float((coord_min[0] + coord_max[0])) / 2 / width
                    ycen = float((coord_min[1] + coord_max[1])) / 2 / height
                    w = float((coord_max[0] - coord_min[0])) / width
                    h = float((coord_max[1] - coord_min[1])) / height

                    # ????????????
                    f.write("%d %.06f %.06f %.06f %.06f\n" % (class_idx, xcen, ycen, w, h))
                    # print(class_idx, xcen, ycen, w, h)
        print('\n')

    def make_namefile(self):
        '''.name?????????????????????'''
        classes_name = os.path.join(self.parentpath, "cfg/classes.name").replace(os.sep, '/')
        pprint(sorted(self.classes.items()))
        pprint(sorted(self.class_count.items()))
        with open(classes_name, "w") as f:
            for key in self.classes:
                # print(key)
                f.write("%s\n" % key)

    def make_datafile(self):
        '''.data?????????????????????'''
        datafile = os.path.join(self.parentpath, 'cfg/test.data').replace(os.sep, '/')
        # paths
        train_path = os.path.join(self.parentpath, 'cfg/train.txt').replace(os.sep, '/')
        valid_path = os.path.join(self.parentpath, 'cfg/valid.txt').replace(os.sep, '/')
        names_path = os.path.join(self.parentpath, 'cfg/classes.name').replace(os.sep, '/')
        backup_path = os.path.join(self.parentpath, 'backup').replace(os.sep, '/')
        with open(datafile, 'w') as f:
            f.write("classes = {}\n".format(len(self.classes)))
            f.write("train = {}\n".format(train_path))
            f.write("valid = {}\n".format(valid_path))
            f.write("names = {}\n".format(names_path))
            f.write("backup = {}\n".format(backup_path))

    def data_split(self):
        '''train,valid,test???????????????'''
        # ????????????
        train_rate = 0.7
        valid_rate = 0.2
        # test_rate = 0.1  # test_rate=1-train_rate-valid_rate

        # ????????????
        imagepath = os.path.join(self.parentpath, 'YoloDataset').replace(os.sep, '/')
        images = glob(imagepath + "/*{}".format(self.ext))
        random.shuffle(images)  # ???????????????

        # ??????
        train_imgs = images[:int(len(images)*train_rate)]
        valid_imgs = images[int(len(images)*train_rate):int(len(images)*(train_rate+valid_rate))]
        test_imgs = images[int(len(images)*(train_rate+valid_rate)):]

        # ????????????
        datas = {'train': train_imgs, 'valid': valid_imgs, 'test': test_imgs}
        for key, value in datas.items():
            txt_path = os.path.join(self.parentpath, 'cfg/{}.txt'.format(key)).replace(os.sep, '/')
            print(f'{key}:{len(value)}')
            with open(txt_path, 'w') as f:
                for image in value:
                    image = image.replace(os.sep, '/')
                    f.write(image+'\n')

    def make_dataset(self):
        '''????????????'''
        self.convert()
        self.make_namefile()
        self.make_datafile()
        self.data_split()


if __name__ == "__main__":
    MakeDataset().make_dataset()
