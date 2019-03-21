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


parser = argparse.ArgumentParser('create image pairs')
parser.add_argument('--fold_A', dest='fold_A', help='input directory for image A', type=str, default='../dataset/50kshoes_edges')
parser.add_argument('--fold_B', dest='fold_B', help='input directory for image B', type=str, default='../dataset/50kshoes_jpg')
parser.add_argument('--fold_AB', dest='fold_AB', help='output directory', type=str, default='../dataset/test_AB')
parser.add_argument('--num_imgs', dest='num_imgs', help='number of images', type=int, default=1000000)
parser.add_argument('--use_AB', dest='use_AB', help='if true: (0001_A, 0001_B) to (0001_AB)', action='store_true')
args = parser.parse_args()

for arg in vars(args):
    print('[%s] = ' % arg, getattr(args, arg))

splits = os.listdir(args.fold_A)

total = len(splits)
for i,sp in enumerate(splits):
    if i%800==0:
        print('processed {:.2f}%'.format(i/total*100))
    img_list = os.path.join(args.fold_A, sp)
    # img_fold_B = os.path.join(args.fold_B, sp)
    # img_list = os.listdir(img_fold_A)
    if args.use_AB:
        img_list = [img_path for img_path in img_list if '_A.' in img_path]

    num_imgs = min(args.num_imgs, len(img_list))
    # print('split = %s, use %d/%d images' % (sp, num_imgs, len(img_list)))
    img_fold_AB = args.fold_AB
    if not os.path.isdir(img_fold_AB):
        os.makedirs(img_fold_AB)
    # print('split = %s, number of images = %d' % (sp, num_imgs))
    for n in range(num_imgs):
        name_A = sp
        path_A = img_list
        if args.use_AB:
            name_B = name_A.replace('_A.', '_B.')
        else:
            name_B = name_A.replace('_edge.png', '.png')
            name_B = name_B.replace('split_', '')
        path_B = os.path.join(args.fold_B, name_B)
        if os.path.isfile(path_A) and os.path.isfile(path_B):
            name_AB = name_A
            if args.use_AB:
                name_AB = name_AB.replace('_A.', '.')  # remove _A
            path_AB = os.path.join(img_fold_AB, name_AB)
            im_A = cv2.imread(path_A, cv2.IMREAD_GRAYSCALE)
            size = im_A.shape[0]
            # im_A[im_A <= 59] = 255
            # im_A[im_A > 59] = 0
            im_A = cv2.cvtColor(im_A, cv2.COLOR_GRAY2BGR)
            im_A = 255 - im_A

            im_B = cv2.imread(path_B, cv2.IMREAD_COLOR)
            im_B = resize(im_B, size, size)
            im_AB = np.concatenate([im_A, im_B], 1)
            if path_AB.endswith('.jpg'):
                cv2.imwrite(path_AB, im_AB, [int(cv2.IMWRITE_JPEG_QUALITY),100])
            else:
                cv2.imwrite(path_AB, im_AB)
