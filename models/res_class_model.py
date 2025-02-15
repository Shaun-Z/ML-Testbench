import torch
import torch.nn as nn
# from util.image_pool import ImagePool
from .base_model import BaseModel
from . import networks

class ResClassModel(BaseModel):

    @staticmethod
    def modify_commandline_options(parser, is_train=True):
        parser.set_defaults(no_dropout=True)  # default model did not use dropout

        parser.add_argument('--num_classes', type=int, default=200, help='the number of output image classes')
        parser.add_argument('--net_name', type=str, default='custom', help='the type of ResNet blocks [custom | resnet18 | resnet34 | resnet50 | resnet101 | resnet152]')
        parser.add_argument('--pool_type', type=str, default='max', help='the type of pooling layer [max | avg]')
        parser.add_argument('--loss_type', type=str, default='cross_entropy', help='the type of loss function [cross_entropy | bcewithlogits]')
        
        return parser
    
    def __init__(self, opt):
        """Initialize the ResNet classificaion class.

        Parameters:
            opt (Option class)-- stores all the experiment flags; needs to be a subclass of BaseOptions
        """
        BaseModel.__init__(self, opt)
        # specify the training losses you want to print out. The training/test scripts will call <BaseModel.get_current_losses>
        self.loss_names = ['Resnet', 'Resnet_val']
        # specify the images you want to save/display. The training/test scripts will call <BaseModel.get_current_visuals>
        # visual_names_A = ['real_A', 'fake_B', 'rec_A']
        # visual_names_B = ['real_B', 'fake_A', 'rec_B']
        # if self.isTrain and self.opt.lambda_identity > 0.0:  # if identity loss is used, we also visualize idt_B=G_A(B) ad idt_A=G_A(B)
        #     visual_names_A.append('idt_B')
        #     visual_names_B.append('idt_A')

        self.visual_names = ['input']  # 
        # specify the models you want to save to the disk. The training/test scripts will call <BaseModel.save_networks> and <BaseModel.load_networks>.
        if self.isTrain:
            self.model_names = ['Resnet_classifier']
        else:  # during test time, only load Gs
            self.model_names = ['Resnet_classifier']

        # define networks (both Generators and discriminators)
        # The naming is different from those used in the paper.
        # Code (vs. paper): G_A (G), G_B (F), D_A (D_Y), D_B (D_X)
        self.netResnet_classifier = networks.define_resnet_classifier(opt.input_nc, opt.num_classes, opt.ngf, opt.net_name, opt.norm, not opt.no_dropout, opt.pool_type, opt.init_type, opt.init_gain, self.gpu_ids)

        if self.isTrain:
            # define loss functions
            if opt.loss_type == 'cross_entropy':
                self.criterion = torch.nn.CrossEntropyLoss()    # Softmax + NLLLoss
            elif opt.loss_type == 'bcewithlogits':
                self.criterion = torch.nn.BCEWithLogitsLoss()   # Sigmoid + BCELoss
            else:
                raise NotImplementedError(f'Loss type {opt.loss_type} is not implemented')
            # initialize optimizers; schedulers will be automatically created by function <BaseModel.setup>.
            self.optimizer = torch.optim.Adam(self.netResnet_classifier.parameters(), lr=opt.lr, betas=(opt.beta1, 0.999))
            self.optimizers.append(self.optimizer)

            self.loss_Resnet_val = 0

    def set_input(self, input):
        """Unpack input data from the dataloader and perform necessary pre-processing steps.

        Parameters:
            input (dict): include the data itself and its metadata information.

        The option 'direction' can be used to swap domain A and domain B.
        """
        self.input = input['X'].to(self.device)
        self.label = input['label'].to(self.device)
        # self.image_paths = input['A_paths' if AtoB else 'B_paths']

    def train(self):
        """Make models train mode during test time"""
        model = self.netResnet_classifier.module if isinstance(self.netResnet_classifier, torch.nn.DataParallel) else self.netResnet_classifier
        for param in model.parameters():
            param.requires_grad = False
        for param in model.layer4.parameters():
            param.requires_grad = False
        for param in model.fc.parameters():
            param.requires_grad = True

    def validate(self, DataLoader_val):
        loss = 0
        self.eval()
        with torch.no_grad():
            for i, data in enumerate(DataLoader_val):
                self.set_input(data)
                self.forward()
                loss += self.criterion(self.output, self.label)
        self.loss_Resnet_val = loss / i
        self.train()

    def forward(self):
        """Run forward pass; called by both functions <optimize_parameters> and <test>."""
        self.output = self.netResnet_classifier(self.input)  # model(input)

    def backward(self):
        """Calculate the loss for back propagation"""
        # First, G_A should fake the discriminator
        self.loss_Resnet = self.criterion(self.output, self.label)
        self.loss_Resnet.backward()

    def optimize_parameters(self):
        """Calculate losses, gradients, and update network weights; called in every training iteration"""
        # forward
        self.forward()      # compute predictions
        self.set_requires_grad([self.netResnet_classifier], True)
        # backward
        self.optimizer.zero_grad()  # set gradients to zero
        self.backward()             # calculate gradients
        self.optimizer.step()       # update weights

    def __call__(self, input):
        """Calculate output of the model"""
        return self.netResnet_classifier(input)
