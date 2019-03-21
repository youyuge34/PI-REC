import os
import numpy as np
import cv2
import argparse
import scipy
import scipy.misc

def resize(img, height, width, centerCrop=True, interp='bilinear'):
    imgh, imgw = img.shape[0:2]

    if centerCrop and imgh != imgw:
        # center crop
        side = np.minimum(imgh, imgw)
        j = (imgh - side) // 2
        i = (imgw - side) // 2
        img = img[j:j + side, i:i + side, ...]
        
    img = scipy.misc.imresize(img, [height, width], interp=interp)
    img = img[:height-height % 4, :width-width % 4, ...]
    return img


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument('-p', '--path', type=str, help='path of model weights files <.pth>')
    parser.add_argument('-e', '--edge', type=str, help='path of edge_file')
    parser.add_argument('-c', '--color', type=str, help='dir path of color domains')
    parser.add_argument('-o', '--output', type=str, help='output dir path')
    # parser.add_argument('-c', '--canny', type=float, default=4, help='sigma of canny')
    # parser.add_argument('-k', '--kmeans', type=int, default=3, help='color numbers of kmeans')
    args = parser.parse_args()

    if not os.path.exists(args.output):
        os.mkdir(args.output)

    for arg in vars(args):
        print('[%s] = ' % arg, getattr(args, arg))

    im_A = cv2.imread(args.edge, cv2.IMREAD_GRAYSCALE)
    size = im_A.shape[0]
    im_A = cv2.cvtColor(im_A, cv2.COLOR_GRAY2BGR)
    im_A = 255 - im_A

    colors = os.listdir(args.color)
    for i,color in enumerate(colors):
        if not (color.endswith('.jpg') or color.endswith('.png')):
            continue
        im_B = cv2.imread(os.path.join(args.color,color), cv2.IMREAD_COLOR)
        im_B = resize(im_B, size, size)
        im_AB = np.concatenate([im_A, im_B], 1)
        path_AB = os.path.join(args.output, color)
        if path_AB.endswith('.jpg'):
            cv2.imwrite(path_AB, im_AB, [int(cv2.IMWRITE_JPEG_QUALITY),100])
        else:
            cv2.imwrite(path_AB, im_AB)