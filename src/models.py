import torch
import torch.nn as nn
from .networks import G_Generator
from .utils import get_model_list


class BaseModel(nn.Module):
    def __init__(self, name, config):
        super(BaseModel, self).__init__()

        self.name = name
        self.config = config
        self.iteration = 0

    def load(self):
        gen_path = get_model_list(self.config.PATH, self.name, 'gen')
        if gen_path is not None:
            print('Loading {} generator weights file: {}...'.format(self.name, gen_path))
            if self.config.DEVICE == torch.device('cuda'):  # gpu
                data = torch.load(gen_path)

            else:  # cpu
                data = torch.load(gen_path, map_location=lambda storage, loc: storage)
            self.generator.load_state_dict(data['generator'])
            self.iteration = data['iteration']


class G_Model(BaseModel):
    def __init__(self, config):
        super(G_Model, self).__init__('G_Model', config)

        # 2nd Phase in paper:
        # generator input: [rgb(3) + edge(1)]
        self.generator = G_Generator()

        # multi-gpu
        if len(config.GPU) > 1:
            self.generator = nn.DataParallel(self.generator, config.GPU)

    def forward(self, edges, color_domain):
        # from torchsummary import summary
        # print(edges.size(),images_masked.size())
        inputs = torch.cat((color_domain, edges), dim=1)
        outputs = self.generator(inputs)  # in: [rgb(3) + edge(1)]
        # print(inputs.size())  #[1,4,128,128]
        # summary(self.generator,input_size=(4, 128, 128))
        return outputs


class R_Model(BaseModel):
    def __init__(self, config):
        super(R_Model, self).__init__('R_Model', config)

        # 2nd Phase in paper:
        # generator input: [rgb(3) + edge(1)]
        self.generator = G_Generator()

        # multi-gpu
        if len(config.GPU) > 1:
            self.generator = nn.DataParallel(self.generator, config.GPU)

    def forward(self, edges, images_blur):
        # from torchsummary import summary
        # print(edges.size(),images_masked.size())
        inputs = torch.cat((images_blur, edges), dim=1)
        outputs = self.generator(inputs)  # in: [rgb(3) + edge(1)]
        # print(inputs.size())  #[1,4,128,128]
        # summary(self.generator,input_size=(4, 128, 128))
        return outputs
