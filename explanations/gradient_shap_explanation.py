import os
import numpy as np
import matplotlib.pyplot as plt
import torch
import torch.nn.functional as F
import torchvision
from torchvision import transforms

from models import create_model
from datasets import create_dataset
from .base_explanation import BaseExplanation
from util.color import red_transparent_blue
from util.util import nhwc_to_nchw, nchw_to_nhwc

from captum.attr import GradientShap

class GradientShapExplanation(BaseExplanation):

    @staticmethod
    def modify_commandline_options(parser):
        # rewrite default values
        parser.add_argument('--std', type=float, default=0.09, help='the standard deviation of the noise used to approximate the integral')
        parser.add_argument('--n_samples', type=int, default=100, help='the number of samples to use to approximate the expectation')
        return parser
    
    def __init__(self, opt):
        super(GradientShapExplanation, self).__init__(opt)
        self.model = create_model(opt)
        self.model.setup(opt)
        self.model.eval()
        self.dataset = create_dataset(opt)

        self.transform= torchvision.transforms.Compose([
            transforms.Lambda(nchw_to_nhwc),
        ])
        self.inv_transform= torchvision.transforms.Compose([
            transforms.Lambda(nhwc_to_nchw),
            transforms.Normalize(
                mean = (-1 * np.array(self.dataset.mean) / np.array(self.dataset.std)).tolist(),
                std = (1 / np.array(self.dataset.std)).tolist()
            ),
            transforms.Lambda(nchw_to_nhwc),
        ])

        self.explainer = self.define_explainer(self.model)

    def define_explainer(self, model):
        gs = GradientShap(model)
        return gs
    
    def explain(self, img_index: int):
        self.image = self.dataset[img_index]['X']
        X = self.image.unsqueeze(0)
        indices = self.dataset[img_index]['indices']
        self.class_list = indices if len(self.opt.index_explain)==0 else self.opt.index_explain

        input_img = X
        baseline = torch.zeros_like(input_img)
        output_indexes = self.class_list
        
        # Compute the attributions
        attributions, delta = self.explainer.attribute (
            input_img.to(self.device),
            stdevs=self.opt.std,
            n_samples=self.opt.n_samples,
            baselines=baseline.to(self.device),
            target=output_indexes,
            return_convergence_delta=True
        )
        
        self.attributions = attributions.cpu().detach().numpy().mean(axis=1)
        
        os.makedirs(f"results/{self.opt.explanation_name}/{self.opt.name}/value", exist_ok=True)
        np.save(f"results/{self.opt.explanation_name}/{self.opt.name}/value/P{img_index}_{indices}.npy", attributions.cpu().detach().numpy())

    def plot(self, save_path: str = None):
        image = self.inv_transform(self.image)

        image_show = image.mean(axis=-1)
        result_show = self.attributions
        labels_to_display = [self.dataset.labels[index] for index in self.class_list]

        fig, axes = plt.subplots(nrows=1, ncols=result_show.shape[0]+1, figsize=(8,6), squeeze=False)
        axes[0, 0].imshow(image)
        axes[0, 0].axis('off')
        max_val = np.nanpercentile(np.abs(result_show), 99.9)
        for i in range(result_show.shape[0]):
            axes[0, i+1].set_title(labels_to_display[i])
            axes[0, i+1].imshow(image_show, cmap=plt.get_cmap('gray'))
            axes[0, i+1].imshow(result_show[i], cmap=red_transparent_blue)
            # axes[0, i+1].imshow(result_show[i], cmap='jet', alpha=0.5)
            axes[0, i+1].axis('off')
            im = axes[0, i+1].imshow(result_show[i], cmap=red_transparent_blue)
            # im = axes[0, i+1].imshow(result_show[i], cmap='jet', alpha=0.5)

        cb = plt.colorbar(im, ax=np.ravel(axes).tolist(), label="Gradient SHAP value", orientation="horizontal", aspect=30)
        cb.outline.set_visible(False)
        

        if save_path is not None:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()