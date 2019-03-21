from __future__ import print_function

import argparse
import glob

import cv2 as cv
import os
import shutil
from src.config import Config
from main import main


def check_load(args):
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


def load_model(config):
    """
    Load model, the key function to interact with backend.
    """
    model = main(mode=5, config=config)
    return model


def model_process(color_domain, edge):
    """
    Key function to reconstruct image from edge and color domain.
    :param color_domain: channel=3
    :param edge: channel=1
    :return: reconstruction
    """
    print(color_domain.shape, edge.shape)
    size_origin = color_domain.shape[:2]
    img = cv.cvtColor(color_domain, cv.COLOR_BGR2RGB)
    result = model.draw(img, edge)
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


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', type=str, help='dir path of model weights files <.pth>')
    parser.add_argument('-e', '--edge', type=str, help='path of edge_file')
    parser.add_argument('-c', '--color', type=str, help='dir path of color domains')
    parser.add_argument('-o', '--output', type=str, help='output dir path')
    args = parser.parse_args()

    if not os.path.exists(args.output):
        os.mkdir(args.output)

    # check the exist of path and the weights files
    config = check_load(args)
    WIN_SIZE = config.INPUT_SIZE
    model = load_model(config)

    colors = os.listdir(args.color)
    for i, color in enumerate(colors):
        if not (color.endswith('.jpg') or color.endswith('.png')):
            continue
        edge, color_domain = inital_pics(args.edge, os.path.join(args.color, color))
        output = model_process(color_domain, edge)
        path = os.path.join(args.output, color)
        path.replace('.jpg', '.png')
        cv.imwrite(path, output)
        print('Output is saved to', path)
