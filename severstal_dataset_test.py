'''
To test this script, run the following command:
----------------
python severstal_dataset_test.py --dataroot ./data/severstal --gpu_ids -1
----------------
or
----------------
python severstal_dataset_test.py -d ./data/severstal -g -1
----------------
'''
import numpy as np
import matplotlib.pyplot as plt

from options.train_options import TrainOptions
from options.test_options import TestOptions
from datasets.severstal_dataset import SeverstalDataset

if __name__ == '__main__':
    
    opt = TrainOptions().parse()
    dataset = SeverstalDataset(opt)

    print(dataset[0]['X'].max(), dataset[0]['X'].min())
    print(dataset[2]['X'].max(), dataset[2]['X'].min())
    print(dataset[3]['X'].max(), dataset[3]['X'].min())
    print(dataset[4]['X'].max(), dataset[4]['X'].min())
    print(dataset[5]['X'].max(), dataset[5]['X'].min())

    for i in range(len(dataset)):
        data = dataset[i]
        Y = data['Y']
        mask = data['Y_mask']
        # print(f"X:{dataset.X[i]}\tY_class:{data['Y_class'].numpy()}\tY:{Y}\t{data['X'].shape}")
        print(f"X:{dataset.X[i]}\tY_class:{data['Y_class']}\tY:{Y}\tY_mask:{mask}")

        plt.figure()
        plt.imshow(data['X'].permute(1,2,0), cmap='gray')
        plt.title('Image')
        plt.axis('off')
        plt.show()
        
        exit()
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