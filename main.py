import os
import cv2
import random
import numpy as np
import torch
import argparse
from shutil import copyfile
from src.config import Config
from src.pi_rec import PiRec


def main(mode=None, config=None):
    r"""starts the model

    Args:
        mode (int): 1: train: TODO
        2: test
        3: refine 2nd phase outputs
        4: test with refinement

        Hidden mode in tool_draw.py:
        5: drawing
        6: Refinement
    """

    if mode == 5 or mode == 6:
        config = load_config_costume(mode, config=config)
    else:
        config = load_config(mode)

    # init environment
    if (config.DEVICE == 1 or config.DEVICE is None) and torch.cuda.is_available():
        os.environ['CUDA_VISIBLE_DEVICES'] = ','.join(str(e) for e in config.GPU)
        config.DEVICE = torch.device("cuda")
        torch.backends.cudnn.benchmark = True  # cudnn auto-tuner
    else:
        config.DEVICE = torch.device("cpu")

    print('DEVICE is:', config.DEVICE)

    # set cv2 running threads to 1 (prevents deadlocks with pytorch dataloader)
    cv2.setNumThreads(0)

    # initialize random seed
    torch.manual_seed(config.SEED)
    torch.cuda.manual_seed_all(config.SEED)
    np.random.seed(config.SEED)
    random.seed(config.SEED)

    # enable the cudnn auto-tuner for hardware.
    torch.backends.cudnn.benchmark = True

    # build the model and initialize
    model = PiRec(config)
    model.load()

    # model training
    if config.MODE == 1:
        config.print()
        print('\nstart training...\n')
        # TODO

    # model test
    elif config.MODE == 2:
        config.print()
        print('\nstart testing...\n')
        with torch.no_grad():
            model.test_G()

    # refine the 2nd phase outputs
    elif config.MODE == 3:
        config.print()
        print('\nstart refine...\n')
        with torch.no_grad():
            model.test_R()

    # 2nd + 3rd phase
    elif config.MODE == 4:
        config.print()
        print('\nstart test with refinement...\n')
        with torch.no_grad():
            model.test_G_R()

    elif config.MODE == 5:
        config.print()
        print('\n############\n###Drawing model loaded.###\n###########\n')
        return model

    elif config.MODE == 6:
        # config.print()
        print('\n############\n###Refinement model loaded.###\n###########\n')
        return model


def load_config(mode=None):
    r"""loads model config 

    Args:
        mode (int): 1: train, 2: test, reads from config file if not specified
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', '--checkpoints', type=str,
                        help='model checkpoints dir path ')

    # test mode
    if mode == 2 or mode == 3 or mode == 4:
        parser.add_argument('--output', type=str, help='path to the output directory')

    args = parser.parse_args()
    config_path = os.path.join(args.path, 'config.yml')

    # create checkpoints path if does't exist
    if not os.path.exists(args.path):
        os.makedirs(args.path)

    # copy config template if does't exist
    if not os.path.exists(config_path):
        copyfile('./config.yml.example', config_path)

    # load config file
    config = Config(config_path)

    # train mode
    if mode == 1:
        config.MODE = 1
        # TODO

    # test mode
    elif mode == 2:
        config.MODE = 2

        if args.output is not None:
            config.RESULTS = args.output

    # refinement mode
    elif mode == 3:
        config.MODE = 3
        if args.output is not None:
            config.RESULTS = args.output

    # test with refinement mode
    elif mode == 4:
        config.MODE = 4
        if args.output is not None:
            config.RESULTS = args.output

    return config


def load_config_costume(mode, config):
    r"""loads model costume config

    Args:
        mode (int): 5: draw
        mode (int): 6: refinement
    """
    print('load_config_demo----->')
    if mode == 5:
        config.MODE = 5
    elif mode == 6:
        config.MODE = 6
    return config
