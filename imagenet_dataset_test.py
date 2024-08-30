'''
To test this script, run the following command:
----------------
python imagenet_dataset_test.py --dataroot ./data/tiny-imagenet --gpu_ids -1
----------------
or
----------------
python imagenet_dataset_test.py -d ./data/tiny-imagenet -g -1
----------------
'''
import numpy as np
import matplotlib.pyplot as plt

from options.train_options import TrainOptions
from datasets.imagenet_dataset import ImageNetDataset
opt = TrainOptions().parse()
dataset = ImageNetDataset(opt)

for i in range(len(dataset)):
    Y = dataset[i]['Y']
    index = dataset[i]['Y_class']
    print(index)
    # if Y == dataset.labels[index]:
    #     # print(dataset[i]['X'].shape)
    #     print(f'{i}\t{Y}\t{index}')
    # else:
    #     print('Error')
    #     exit()

print(len(dataset.labels), len(dataset.labels_meaning))

# for i in range(10):
#     plt.subplot(2, 5, i+1)
#     plt.imshow(dataset[i]['X'].permute(1,2,0), cmap='gray')
#     plt.title(dataset.labels_meaning[dataset[i]['Y']])
#     plt.axis('off')
# plt.show()