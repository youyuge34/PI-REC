import os
import glob
import scipy
import torch
import random
import numpy as np
import torchvision.transforms.functional as F
from torch.utils.data import DataLoader
from PIL import Image
from scipy.misc import imread
from skimage.feature import canny
from skimage.color import rgb2gray
from .utils import img_kmeans
import cv2 as cv


class Dataset(torch.utils.data.Dataset):
    def __init__(self, config, flist, augment=False, training=False):
        super(Dataset, self).__init__()
        self.augment = augment
        self.training = training
        self.data = self.load_flist(flist)

        self.input_size = config.INPUT_SIZE
        self.sigma = config.SIGMA
        self.km = config.KM

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        try:
            item = self.load_item(index)
        except:
            print('loading error: ' + self.data[index])
            item = self.load_item(0)

        return item

    def load_name(self, index):
        name = self.data[index]
        return os.path.basename(name)

    def load_item(self, index):

        size = self.input_size

        # load image
        img = imread(self.data[index])

        # resize/crop if needed
        if size != 0:
            img = self.resize(img, size, size)

        # create grayscale image
        img_gray = rgb2gray(img)

        # load edge
        edge = self.load_edge(img_gray, index)

        # augment data
        if self.augment and np.random.binomial(1, 0.5) > 0:
            img = img[:, ::-1, ...]
            img_gray = img_gray[:, ::-1, ...]
            edge = edge[:, ::-1, ...]

        # To get color domain
        # random_blur = 2 * np.random.randint(7, 18) + 1
        random_blur = 25
        img_color_domain = cv.medianBlur(img, random_blur)
        K = self.km
        # K = np.random.randint(2, 6)
        img_color_domain = img_kmeans(img_color_domain, K)
        # img_blur = cv.medianBlur(img_blur, np.random.randint(1, 4) * 2 - 1)
        img_color_domain = cv.medianBlur(img_color_domain, 3)

        return self.to_tensor(img), self.to_tensor(img_gray), self.to_tensor(edge), self.to_tensor(img_color_domain)

    def load_edge(self, img, index):
        # random_sigma = np.random.randint(25, 55) / 10.
        sigma = self.sigma

        # canny
        # no edge
        if sigma == -1:
            return np.zeros(img.shape).astype(np.float)

        # random sigma
        if sigma == 0:
            sigma = random.randint(1, 4)

        return canny(img, sigma=sigma, mask=None).astype(np.float)

    def to_tensor(self, img):
        img = Image.fromarray(img)
        img_t = F.to_tensor(img).float()
        return img_t

    def resize(self, img, height, width, centerCrop=True, interp='bilinear'):
        imgh, imgw = img.shape[0:2]

        if centerCrop and imgh != imgw:
            # center crop
            side = np.minimum(imgh, imgw)
            j = (imgh - side) // 2
            i = (imgw - side) // 2
            img = img[j:j + side, i:i + side, ...]

        img = scipy.misc.imresize(img, [height, width], interp=interp)

        return img

    def load_flist(self, flist):
        if isinstance(flist, list):
            return flist

        # flist: image file path, image directory path, text file flist path
        if isinstance(flist, str):
            if os.path.isdir(flist):
                flist = list(glob.glob(flist + '/*.jpg')) + list(glob.glob(flist + '/*.png'))
                flist.sort()
                return flist

            if os.path.isfile(flist):
                try:
                    return np.genfromtxt(flist, dtype=np.str, encoding='utf-8')
                except:
                    return [flist]

        return []

    def create_iterator(self, batch_size):
        while True:
            sample_loader = DataLoader(
                dataset=self,
                batch_size=batch_size,
                drop_last=True
            )

            for item in sample_loader:
                yield item
