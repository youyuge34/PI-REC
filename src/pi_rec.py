import os

import numpy as np
from torch.utils.data import DataLoader
from .dataset import Dataset
from .models import G_Model, R_Model
from .utils import resize, create_dir, imsave, to_tensor, output_align


class PiRec():
    def __init__(self, config):
        self.config = config

        self.debug = False
        if config.MODE == 2 or config.MODE == 5:
            self.g_model = G_Model(config).to(config.DEVICE)
        elif config.MODE == 6 or config.MODE == 3:
            self.r_model = R_Model(config).to(config.DEVICE)
        elif config.MODE == 4:
            self.g_model = G_Model(config).to(config.DEVICE)
            self.r_model = R_Model(config).to(config.DEVICE)

        # test mode ( w/ or w/o refinement)
        if self.config.MODE == 2 or config.MODE == 4:
            self.test_dataset = Dataset(config, config.TEST_FLIST,
                                        augment=False, training=False)

        # refinement mode from command line
        if self.config.MODE == 3:
            self.refine_dataset = Dataset(config, config.REFINE_FLIST,
                                        augment=False, training=False)


        # self.samples_path = os.path.join(config.PATH, 'samples')
        self.results_path = os.path.join(config.PATH, 'results_2nd')
        self.results_path = os.path.join(self.results_path, 'km_{}_sigma_{}'.format(config.KM, config.SIGMA))

        self.refine_path = os.path.join(config.PATH, 'results_3rd')

        if config.MODE == 4:
            self.results_path = os.path.join(config.PATH, 'results_2nd_3rd')
            self.results_path = os.path.join(self.results_path, 'km_{}_sigma_{}'.format(config.KM, config.SIGMA))
        if config.RESULTS is not None:
            self.results_path = os.path.join(config.RESULTS)
            self.refine_path = os.path.join(config.RESULTS)

        if config.DEBUG is not None and config.DEBUG != 0:
            self.debug = True

    def load(self):
        if self.config.MODE == 2 or self.config.MODE == 5:
            self.g_model.load()
        elif self.config.MODE == 6 or self.config.MODE == 3:
            self.r_model.load()
        elif self.config.MODE == 4:
            self.g_model.load()
            self.r_model.load()

    def test_G(self):
        self.g_model.eval()

        create_dir(self.results_path)

        test_loader = DataLoader(
            dataset=self.test_dataset,
            batch_size=1,
        )

        index = 0
        for items in test_loader:
            name = self.test_dataset.load_name(index)
            images, images_gray, edges, color_domain = self.cuda(*items)
            # print('images size is {}, \n edges size is {}, \n color_domain size is {}'.format(images.size(), edges.size(), color_domain.size()))
            index += 1

            outputs = self.g_model(edges, color_domain)
            outputs = output_align(images, outputs)
            outputs_merged = outputs

            output = self.postprocess(outputs_merged)[0]
            path = os.path.join(self.results_path, name)
            print(index, name)

            imsave(output, path)

            if self.debug:
                images_input = self.postprocess(images)[0]
                edges = self.postprocess(edges)[0]
                color_domain = self.postprocess(color_domain)[0]
                fname, fext = name.split('.')
                fext = 'png'
                imsave(images_input, os.path.join(self.results_path, fname + '_input.' + fext))
                imsave(edges, os.path.join(self.results_path, fname + '_edge.' + fext))
                imsave(color_domain, os.path.join(self.results_path, fname + '_color_domain.' + fext))

        print('\nEnd test....')

    def test_R(self):
        self.r_model.eval()

        create_dir(self.refine_path)

        test_loader = DataLoader(
            dataset=self.refine_dataset,
            batch_size=1,
        )

        index = 0
        for items in test_loader:
            name = self.refine_dataset.load_name(index)
            images, images_gray, edges, _ = self.cuda(*items)
            # print('images size is {}, \n edges size is {}, \n color_domain size is {}'.format(images.size(), edges.size(), color_domain.size()))
            index += 1

            outputs = self.r_model(edges, images)
            outputs = output_align(images, outputs)
            outputs_merged = outputs

            output = self.postprocess(outputs_merged)[0]
            path = os.path.join(self.refine_path, name)
            print(index, name)

            imsave(output, path)

            if self.debug:
                images_input = self.postprocess(images)[0]
                edges = self.postprocess(edges)[0]
                # color_domain = self.postprocess(color_domain)[0]
                fname, fext = name.split('.')
                fext = 'png'
                imsave(images_input, os.path.join(self.refine_path, fname + '_input.' + fext))
                imsave(edges, os.path.join(self.refine_path, fname + '_edge.' + fext))
                # imsave(color_domain, os.path.join(self.results_path, fname + '_color_domain.' + fext))

        print('\nEnd refinement....')

    def test_G_R(self):
        self.g_model.eval()
        self.r_model.eval()

        create_dir(self.results_path)

        test_loader = DataLoader(
            dataset=self.test_dataset,
            batch_size=1,
        )

        index = 0
        for items in test_loader:
            name = self.test_dataset.load_name(index)
            images, images_gray, edges, color_domain = self.cuda(*items)
            # print('images size is {}, \n edges size is {}, \n color_domain size is {}'.format(images.size(), edges.size(), color_domain.size()))
            index += 1

            outputs = self.g_model(edges, color_domain)
            outputs = output_align(images, outputs)
            outputs_merged = outputs

            output = self.postprocess(outputs_merged)[0]
            path = os.path.join(self.results_path, name)
            print(index, name)

            imsave(output, path)

            if self.debug:
                images_input = self.postprocess(images)[0]
                edge = self.postprocess(edges)[0]
                color_domain = self.postprocess(color_domain)[0]
                fname, fext = name.split('.')
                fext = 'png'
                imsave(images_input, os.path.join(self.results_path, fname + '_input.' + fext))
                imsave(edge, os.path.join(self.results_path, fname + '_edge.' + fext))
                imsave(color_domain, os.path.join(self.results_path, fname + '_color_domain.' + fext))

            img_blur = outputs
            # img_blur = self.cuda(img_blur)
            outputs = self.r_model(edges, img_blur)

            output = self.postprocess(outputs)[0]
            # output = outputs.cpu().numpy().astype(np.uint8).squeeze()
            fname, fext = name.split('.')
            fext = 'png'
            imsave(output, os.path.join(self.results_path, fname + '_refine.' + fext))

        print('\nEnd test with refinement....')

    def draw(self, color_domain, edge):
        self.g_model.eval()
        size = self.config.INPUT_SIZE
        color_domain = resize(color_domain, size, size, interp='lanczos')
        edge = resize(edge, size, size, interp='lanczos')
        edge[edge <= 69] = 0
        edge[edge > 69] = 255

        color_domain = to_tensor(color_domain)
        edge = to_tensor(edge)

        color_domain, edge = self.cuda(color_domain, edge)

        if self.config.DEBUG:
            print('In model.draw():---> \n color domain size is {}, edges size is {}'.format(color_domain.size(),
                                                                                             edge.size()))
        outputs = self.g_model(edge, color_domain)

        outputs = self.postprocess(outputs)[0]
        output = outputs.cpu().numpy().astype(np.uint8).squeeze()
        edge = self.postprocess(edge)[0]
        edge = edge.cpu().numpy().astype(np.uint8).squeeze()

        return output

    def refine(self, img_blur, edge):
        self.r_model.eval()
        size = self.config.INPUT_SIZE
        # color_domain = resize(color_domain, size, size, interp='lanczos')
        edge = resize(edge, size, size, interp='lanczos')
        edge[edge <= 69] = 0
        edge[edge > 69] = 255

        img_blur = to_tensor(img_blur)
        edge = to_tensor(edge)

        img_blur, edge = self.cuda(img_blur, edge)

        if self.config.DEBUG:
            print('In model.refine():---> \n img_blur size is {}, edges size is {}'.format(img_blur.size(),
                                                                                             edge.size()))
        outputs = self.r_model(edge, img_blur)

        outputs = self.postprocess(outputs)[0]
        output = outputs.cpu().numpy().astype(np.uint8).squeeze()
        edge = self.postprocess(edge)[0]
        edge = edge.cpu().numpy().astype(np.uint8).squeeze()

        return output

    def cuda(self, *args):
        return (item.to(self.config.DEVICE) for item in args)

    def postprocess(self, img):
        # [0, 1] => [0, 255]
        img = img * 255.0
        img = img.permute(0, 2, 3, 1)
        return img.int()
