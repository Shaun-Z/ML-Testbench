# %% Explain Resnet18 on ImageNet using SHAP
'''
python explain.py -d ./data/tiny-imagenet -n CustomClassifier -g 0 -m res_class --net_name custom --dataset_name imagenet --eval --explanation_name shap --epoch 15
'''
# %% Explain Resnet50 on ImageNet using BHEM
'''
python explain.py -d ./data/tiny-imagenet -n Resnet50onImageNet -g mps -m res_class --net_name resnet50 --dataset_name imagenet --eval --explanation_name bhem --epoch 15
'''
# %% Explain Resnet18 on ImageNet using SHAP
'''
python explain.py -d ./data/tiny-imagenet -n Resnet18onImageNet -g mps -m res_class --net_name resnet18 --dataset_name imagenet --eval --explanation_name shap --epoch 25
'''
# %% Explain Resnet50 on PASCAL_VOC_2012 using BHEM
'''
python explain.py -d ./data/pascal_voc_2012 -n Resnet50onPASCAL -g mps -m res_class --net_name resnet50 --dataset_name pascalvoc2012 --eval --explanation_name bhem --epoch best --loss_type bcewithlogits --segmentation --approx
'''

# %% The following explanations have been implemented in config files
'''
python explain.py --config config/CNNonBrainMRI/explain.yaml
python explain.py --config config/CNNonIcons50/explain.yaml
'''

import time
from tqdm import tqdm
from options.explain_options import ExplainOptions
from explanations import create_explanation, aopc

if __name__ == '__main__':
    opt = ExplainOptions().parse()   # get explain options

    # set indexes for explanation
    opt.index_explain = [int(i) for i in opt.index_explain]

    explainer = create_explanation(opt)

    # img_index = 209
    # time_stamp = time.time()
    # explainer.explain(img_index) # 1, 5
    # print(f"Computation time: \033[92m{(time.time() - time_stamp)}\033[0m s")
    # # aopc.get_single_aopc_value(explainer.predict, explainer.dataset, img_index, opt.explanation_name, opt.name)

    # Y_class = explainer.dataset[img_index]['label']
    # indices = explainer.dataset[img_index]['indices']
    # print(Y_class, indices)

    # # explainer.plot(save_path=f"results/{opt.explanation_name}/{opt.name}/image/P{img_index}_{Y}.png")
    # explainer.plot()

    if len(opt.index_instance)==0:  # if instance index not specified, explain all instances
        for img_index in tqdm(range(len(explainer.dataset))):
            indices = explainer.dataset[img_index]['indices']
            # print(indices)
            Y = [explainer.dataset.labels[i] for i in indices]
            # print(indices, Y)
            explainer.explain(img_index)
            # explainer.plot(save_path=f"results/{opt.explanation_name}/{opt.name}/image/P{img_index}_{Y}.png")
            explainer.plot(save_path=f"results/{opt.explanation_name}/{opt.name}/image/P{img_index}_{indices}.png")
    else:
        for img_index in tqdm(opt.index_instance):
            indices = explainer.dataset[img_index]['indices']
            # print(img_index, indices, len(explainer.dataset.labels))
            # Y = [explainer.dataset.labels[i] for i in indices]
            explainer.explain(img_index)
            explainer.plot(save_path=f"results/{opt.explanation_name}/{opt.name}/image/P{img_index}_{indices}.png")
        # aopc.get_single_aopc_value(explainer.predict, explainer.dataset, img_index, opt.explanation_name, opt.name)

    # aopc.get_average_aopc_value(opt.explanation_name, opt.name)