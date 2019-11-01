#!/usr/bin/env python
# author: youyuge34@github
"""
===============================================================================
Interactive Image Drawing tool of PI-REC.

Paper: PI-REC: Progressive Image Reconstruction Network With Edge and Color Domain 2019.3

Command:
    python tool_draw.py --path <your weights directory path> -r

README FIRST:
    Four windows will show up, one for color domain, one for edge, one for output and a pane.
    [Important] Switch your typewriting into ENG first.


Key | Description

Mouse `Left` | Draw
Mouse `Right` | Erase
Key `h` | Show the help message box.
Key `[` | To make the brush thickness smaller
Key `]` | To make the brush thickness larger
Key `g` | To reconstruct the image from edge and color domain
Key `u` | To refine the output only when `-r` is added in command line
Key `Alt` | To absorb mouse pointer color in color domain (the mouse must be moving at the same time)
Key `x` | To save the binary edge
Key `c` | To save the color domain
Key `s` | To save the output
Key `q` | To quit

                #####################################
                #####  Author: youyuge34@github  ####
                #####    License-CC BY·NC 4.0    ####
                #####################################
===============================================================================
"""

# Python 2/3 compatibility
from __future__ import print_function

import argparse
import glob

from easygui import *
import numpy as np
import cv2 as cv
import os
import shutil
from src.config import Config
from main import main
from src.utils import resize, img_kmeans
from skimage.feature import canny
from skimage.color import rgb2gray

BLUE = [148, 195, 222]  # rectangle color
RED = [0, 0, 255]  # PR BG
GREEN = [0, 255, 0]  # PR FG
BLACK = [0, 0, 0]  # sure BG
WHITE = [255, 255, 255]  # sure FG
PANE = [0, 0, 0]

DRAW_MASK = {'color': RED, 'val': 255}

radius = 3  # color_domain radius
drawing = False
drawing_edge_l = False
drawing_edge_r = False
drawing_color_domain_l = False
drawing_color_domain_r = False
value = DRAW_MASK
eraser_mode = False
THICKNESS = -1  # solid color_domain circle 实心圆


def nothing(x):
    pass


def onmouse_color_domain(event, x, y, flags, param):
    """
    mouse callback function, whenever mouse move or click in input window this function is called.
    只要鼠标在color_domain窗口上移动(点击），此函数就会被回调执行
    """
    # to change the variable outside of the function
    # 为方法体外的变量赋值，声明global
    global drawing_color_domain_l, drawing_color_domain_r, value, color_domain, PANE
    # print(x,y)

    # draw touchup curves
    if event == cv.EVENT_LBUTTONDOWN and not eraser_mode:
        drawing_color_domain_l = True
        cv.circle(color_domain, (x, y), radius, PANE, THICKNESS, lineType=cv.LINE_4)

    elif drawing_color_domain_l is True and event == cv.EVENT_MOUSEMOVE:
        cv.circle(color_domain, (x, y), radius, PANE, THICKNESS, lineType=cv.LINE_4)

    elif drawing_color_domain_l is True and event == cv.EVENT_LBUTTONUP:
        drawing_color_domain_l = False
        cv.circle(color_domain, (x, y), radius, PANE, THICKNESS, lineType=cv.LINE_4)

    elif event == cv.EVENT_RBUTTONDOWN or (event == cv.EVENT_LBUTTONDOWN and eraser_mode):
        drawing_color_domain_r = True
        cv.circle(color_domain, (x, y), radius, WHITE, THICKNESS, lineType=cv.LINE_AA)

    elif drawing_color_domain_r is True and event == cv.EVENT_MOUSEMOVE:
        cv.circle(color_domain, (x, y), radius, WHITE, THICKNESS, lineType=cv.LINE_AA)

    elif drawing_color_domain_r is True and (event == cv.EVENT_RBUTTONUP or event == cv.EVENT_LBUTTONUP):
        drawing_color_domain_r = False
        cv.circle(color_domain, (x, y), radius, WHITE, THICKNESS, lineType=cv.LINE_AA)

    elif flags == cv.EVENT_FLAG_ALTKEY:
        # print(flags)
        color = color_domain[y, x]
        cv.setTrackbarPos('B', 'pane', color[0])
        cv.setTrackbarPos('G', 'pane', color[1])
        cv.setTrackbarPos('R', 'pane', color[2])


def onmouse_edge(event, x, y, flags, param):
    """
    mouse callback function, whenever mouse move or click in edge window this function is called.
    只要鼠标在edge窗口上移动(点击），此函数就会被回调执行
    """
    # to change the variable outside of the function
    # 为方法体外的变量赋值，声明global
    global drawing_edge_l, drawing_edge_r, value, edge
    # print('x:',x,'  y:', y)

    # draw touchup curves
    if event == cv.EVENT_LBUTTONDOWN and not eraser_mode:
        drawing_edge_l = True
        # cv.circle(edge, (x, y), 1, WHITE, THICKNESS, lineType=cv.LINE_AA)
        edge[y, x] = 255

    elif drawing_edge_l is True and event == cv.EVENT_MOUSEMOVE:
        # cv.circle(edge, (x, y), 1, WHITE, THICKNESS, lineType=cv.LINE_4)
        edge[y, x] = 255
        # if edge[y-1,x] == 0 and edge[y,x-1] == 0 and edge[y+1,x] == 0 and edge[y,x+1] == 0:
        #     if edge[x]

    elif drawing_edge_l is True and event == cv.EVENT_LBUTTONUP:
        drawing_edge_l = False
        # cv.circle(edge, (x, y), 1, WHITE, THICKNESS, lineType=cv.LINE_AA)
        edge[y, x] = 255

    elif event == cv.EVENT_RBUTTONDOWN or (event == cv.EVENT_LBUTTONDOWN and eraser_mode):
        drawing_edge_r = True
        cv.circle(edge, (x, y), radius, BLACK, THICKNESS, lineType=cv.LINE_AA)

    elif drawing_edge_r is True and event == cv.EVENT_MOUSEMOVE:
        cv.circle(edge, (x, y), radius, BLACK, THICKNESS, lineType=cv.LINE_AA)

    elif drawing_edge_r is True and (event == cv.EVENT_RBUTTONUP or event == cv.EVENT_LBUTTONUP):
        drawing_edge_r = False
        cv.circle(edge, (x, y), radius, BLACK, THICKNESS, lineType=cv.LINE_AA)


def check_load_G(args):
    """
    Check the directory and weights files. Load the config file.
    """
    if not os.path.exists(args.path):
        raise NotADirectoryError('Path <' + str(args.path) + '> does not exist!')

    G_weight_files = list(glob.glob(os.path.join(args.path, 'G_Model_gen*.pth')))
    if len(G_weight_files) == 0:
        raise FileNotFoundError('Weights file <G_Model_gen*.pth> cannot be found under path: ' + args.path)

    config_path = os.path.join(args.path, 'config.yml')
    # copy config template if does't exist
    if not os.path.exists(config_path):
        shutil.copyfile('./config.yml.example', config_path)

    # load config file
    config = Config(config_path)

    return config


def check_load_R(args):
    """
    Check the directory and weights files. Load the config file.
    """

    R_weight_files = list(glob.glob(os.path.join(args.path, 'R_Model_gen*.pth')))
    if len(R_weight_files) == 0:
        raise FileNotFoundError('Weights file <R_Model_gen*.pth> cannot be found under path: ' + args.path)

    config_path = os.path.join(args.path, 'config.yml')

    # load config file
    config = Config(config_path)

    return config


def load_model_G(config):
    """
    Load generate phase model, the key function to interact with backend.
    """
    model = main(mode=5, config=config)
    return model


def load_model_R(config):
    """
    Load refinement phase model, the key function to interact with backend.
    """
    model = main(mode=6, config=config)
    return model


def model_process(color_domain, edge):
    """
    Key function to reconstruct image from edge and color domain.
    :param color_domain: channel=3
    :param edge: channel=1
    :return: reconstruction
    """
    # print(color_domain.shape, edge.shape)
    size_origin = color_domain.shape[:2]
    img = cv.cvtColor(color_domain, cv.COLOR_BGR2RGB)
    result = model_G.draw(img, edge)
    result = cv.resize(result, size_origin)
    result = cv.cvtColor(result, cv.COLOR_RGB2BGR)
    return result


def model_refine(img_blur, edge):
    """
    Key function to refine image from 2nd phase output.
    :param img_blur: channel=3
    :param edge: channel=1
    :return: refinement
    """
    # print(color_domain.shape, edge.shape)
    size_origin = img_blur.shape[:2]
    img_blur = cv.cvtColor(img_blur, cv.COLOR_BGR2RGB)
    result = model_R.refine(img_blur, edge)
    result = cv.resize(result, size_origin)
    result = cv.cvtColor(result, cv.COLOR_RGB2BGR)
    return result


def inital_pics(edge_file, color_domain_file):
    edge_file = cv.imread(edge_file, cv.IMREAD_GRAYSCALE)
    edge_file = cv.resize(edge_file, (WIN_SIZE, WIN_SIZE), interpolation=cv.INTER_LANCZOS4)
    edge_file[edge_file <= 59] = 0
    edge_file[edge_file > 59] = 255
    color_domain_file = cv.imread(color_domain_file)
    color_domain_file = cv.resize(color_domain_file, (WIN_SIZE, WIN_SIZE))
    return edge_file, color_domain_file


def inital_colorful_pic(file, sigma, kmeans):
    img = cv.imread(file)
    img = resize(img, WIN_SIZE, WIN_SIZE, )
    img_gray = rgb2gray(img)

    # edge
    out_edge = canny(img_gray, sigma=float(sigma), mask=None).astype(np.uint8)
    out_edge[out_edge == 1] = 255
    # color_domain
    # random_blur = 2 * np.random.randint(7, 18) + 1
    out_blur = cv.medianBlur(img, 23)
    # K = np.random.randint(2, 6)
    out_blur = img_kmeans(out_blur, int(kmeans))
    out_blur = cv.medianBlur(out_blur, np.random.randint(1, 4) * 2 - 1)
    return out_edge, out_blur


def lighter(output):
    alpha = 1.1
    res = np.uint8(np.clip((alpha * output + 125*(1-alpha)), 0, 255))
    # (b, g, r) = cv.split(output)
    # bH = cv.equalizeHist(b)
    # gH = cv.equalizeHist(g)
    # rH = cv.equalizeHist(r)
    # # 合并每一个通道
    # res = cv.merge((bH, gH, rH))
    return res


if __name__ == '__main__':

    # print documentation
    print(__doc__)

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', type=str, help='path of model weights files <.pth>')
    parser.add_argument('-c', '--canny', type=float, default=3, help='sigma of canny')
    parser.add_argument('-k', '--kmeans', type=int, default=3, help='color numbers of kmeans')
    parser.add_argument('-r', '--refinement', action='store_true', help='load refinement model')
    args = parser.parse_args()

    # check the exist of path and the weights files
    config = check_load_G(args)
    model_G = load_model_G(config)
    model_R = None

    if args.refinement:
        config = check_load_R(args)
        model_R = load_model_R(config)

    WIN_SIZE = config.INPUT_SIZE

    edge = np.zeros([WIN_SIZE, WIN_SIZE], dtype=np.uint8)  # 256 x 256
    color_domain = np.zeros([WIN_SIZE, WIN_SIZE, 3], dtype=np.uint8)
    color_domain += 255  # turn white
    output = np.zeros(color_domain.shape, np.uint8)  # output image to be shown

    MODE = buttonbox("Choose your model:\n 1:draw from empty \n 2:draw from color_domain and edge \n 3:draw from pic",
                     choices=("1", "2", "3", "cancel"),
                     title="PI-REC")
    if MODE == "1":
        pass
    elif MODE == "2":
        msgbox("Choose an edge picture", title="PI-REC")
        edge_file = fileopenbox(msg='Select an edge', title='PI-REC', filetypes=[['*.png', '*.jpg', 'Image Files']])
        if not edge_file.endswith('.jpg') and not edge_file.endswith('.png'):
            exit("edge file must be .jpg or .png")
        msgbox("Choose a color_domain picture", title="PI-REC")
        color_domain_file = fileopenbox(msg='Select a color_domain', title='PI-REC',
                                        filetypes=[['*.png', '*.jpg', 'Image Files']])
        if not color_domain_file.endswith('.jpg') and not color_domain_file.endswith('.png'):
            exit("color_domain file must be .jpg or .png")
        edge, color_domain = inital_pics(edge_file, color_domain_file)
        # print(edge.shape, color_domain.shape, type(edge), type(color_domain))
    elif MODE == "3":
        msgbox("Choose a colorful picture", title="PI-REC")
        pic_file = fileopenbox(msg='Select an edge', title='PI-REC', filetypes=[['*.png', '*.jpg', 'Image Files']])
        if not pic_file.endswith('.jpg') and not pic_file.endswith('.png'):
            exit("edge file must be .jpg or .png")
        edge, color_domain = inital_colorful_pic(pic_file, args.canny, args.kmeans)
        # print(edge.shape, color_domain.shape, type(edge), type(color_domain))
        # print(edge[64])
    else:
        exit(0)

    # input and output windows
    cv.namedWindow('edge', cv.WINDOW_NORMAL)
    cv.namedWindow('color_domain', cv.WINDOW_NORMAL)
    cv.namedWindow('output', cv.WINDOW_NORMAL)
    cv.setMouseCallback('edge', onmouse_edge)
    cv.setMouseCallback('color_domain', onmouse_color_domain)
    cv.moveWindow('color_domain', edge.shape[1] + 20, 90)
    cv.moveWindow('output', edge.shape[1] + 80, 280)

    # Create a black image, a window
    pane = np.zeros((128, 420, 3), np.uint8)
    cv.namedWindow('pane')
    # create trackbars for color change
    cv.createTrackbar('R', 'pane', 0, 255, nothing)
    cv.createTrackbar('G', 'pane', 0, 255, nothing)
    cv.createTrackbar('B', 'pane', 0, 255, nothing)
    cv.moveWindow('pane', edge.shape[1] + 120, 370)

    while 1:
        cv.imshow('output', output)
        cv.imshow('edge', edge)
        temp_edge = np.concatenate([edge[:, :, np.newaxis], edge[:, :, np.newaxis], edge[:, :, np.newaxis]], axis=2)
        cv.imshow('color_domain', cv.add(temp_edge, color_domain, mask=255 - edge))

        # get current positions of four trackbars
        r = cv.getTrackbarPos('R', 'pane')
        g = cv.getTrackbarPos('G', 'pane')
        b = cv.getTrackbarPos('B', 'pane')
        pane[:] = [b, g, r]
        PANE = [b, g, r]
        cv.imshow('pane', pane)
        k = cv.waitKey(5)

        # key bindings
        if k == 27 or k == ord('q'):  # esc to exit
            break

        if k == ord('r'):  # reset everything
            print("resetting \n")
            radius = 3
            edge = np.zeros([WIN_SIZE, WIN_SIZE], dtype=np.uint8)  # 256 x 256
            color_domain = np.zeros([WIN_SIZE, WIN_SIZE, 3], dtype=np.uint8)
            color_domain += 255  # turn white
            output = np.zeros(color_domain.shape, np.uint8)  # output image to be shown
            drawing_edge_l = False
            drawing_edge_r = False
            drawing_color_domain_l = False
            drawing_color_domain_r = False
            if MODE == "2":
                edge, color_domain = inital_pics(edge_file, color_domain_file)

        # elif k == ord('n'):  # begin to path the image
        #     print('\ncolor_domain cleared')
        #     color_domain = np.zeros([WIN_SIZE, WIN_SIZE, 3], dtype=np.uint8)
        #     color_domain += 255
        #     color_domain = show_edge_on_color_domain(color_domain, edge)
        #
        #     print("\nEdge saved and shown")

        elif k == ord('g'):
            print("\nDrawing using color domain and edge...")
            output = model_process(color_domain, edge)
            print("\nFinished!")
        elif k == ord('['):
            radius = 1 if radius == 1 else radius - 1
            print('Brush thickness is', radius)
        elif k == ord(']'):
            radius += 1
            print('Brush thickness is', radius)
        elif k == ord('s'):
            path = filesavebox('save', 'save the output.', default='draw_output.png',
                               filetypes=[['*.jpg', 'jpg'], ['*.png', 'png']])
            if path:
                if not path.endswith('.jpg') and not path.endswith('.png'):
                    path = str(path) + '.png'
                cv.imwrite(path, output)
                print('Drawing output is saved to', path)
        elif k == ord('c'):
            path = filesavebox('save', 'save the color domain.', default='draw_color_domain.png',
                               filetypes=[['*.jpg', 'jpg'], ['*.png', 'png']])
            if path:
                if not path.endswith('.jpg') and not path.endswith('.png'):
                    path = str(path) + '.png'
                cv.imwrite(path, color_domain)
                print('Drawing color domain is saved to', path)
        elif k == ord('x'):
            path = filesavebox('save', 'save the edge.', default='draw_edge.png',
                               filetypes=[['*.jpg', 'jpg'], ['*.png', 'png']])
            if path:
                if not path.endswith('.jpg') and not path.endswith('.png'):
                    path = str(path) + '.png'
                # img = scipy.misc.imresize(edge, [config.INPUT_SIZE, config.INPUT_SIZE], interp='lanczos')
                # img[img <= 59] = 0
                # img[img > 59] = 255
                # cv.imwrite(path, cv.resize(edge,(128,128),interpolation=cv.INTER_NEAREST))
                cv.imwrite(path, edge)
                print('Drawing edge is saved to', path)
        elif k == ord('h'):
            msgbox(__doc__, title="PI-REC")
        elif k == ord('u'):
            if model_R is not None:
                print("\nRefinement using output and edge...")
                output = model_refine(output, edge)
                print("\nFinished!")
        elif k == ord('l'):
            output = lighter(output)
        elif k == ord('e'):
            eraser_mode = not eraser_mode

    cv.destroyAllWindows()
