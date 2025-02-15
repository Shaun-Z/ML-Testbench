# %% Train resnet model on tiny-imagenet dataset
'''
python train.py -d ./data/tiny-imagenet -n Resnet101onImageNet -g 0 -m res_class --net_name resnet101 --dataset_name imagenet --batch_size 512 --lr 0.0002 --n_epochs 20 --n_epochs_decay 20 --use_wandb
'''
# %% Train resnet model on pascalvoc dataset
'''
python train.py -d ./data/pascal_voc_2012 -n Resnet18onPASCAL -g 0 -m res_class --net_name resnet18 --dataset_name pascalvoc2012 --loss_type bcewithlogits --batch_size 64 --lr 0.0002 --n_epochs 20 --n_epochs_decay 20 --use_wandb
'''
# %% Train custom model
'''
python train.py -d ./data/tiny-imagenet -n CustomClassifier -g 0 -m res_class --net_name custom --dataset_name imagenet --batch_size 512 --lr 0.0002 --n_epochs 20 --n_epochs_decay 20 --use_wandb
'''
# %%
import time
from tqdm import tqdm
from options.train_options import TrainOptions
from datasets import create_dataloader
from models import create_model
from util.visualizer import Visualizer

if __name__ == '__main__':
    opt = TrainOptions().parse()   # get training options
    dataloader = create_dataloader(opt)  # create a dataset given opt.dataset_mode and other options
    dataset_size = len(dataloader)    # get the number of items in the dataset.
    print(f'The number of training items = \033[92m{dataset_size}\033[0m')

    model = create_model(opt)      # create a model given opt.model and other options
    model.setup(opt)               # regular setup: load and print networks; create schedulers
    visualizer = Visualizer(opt)   # create a visualizer that display/save images and plots
    total_iters = 0                # the total number of training iterations

    opt.phase = 'val'
    dataloader_val = create_dataloader(opt)  # create a dataset given opt.dataset_mode and other options
    print(f'The number of validation items = \033[92m{len(dataloader_val)}\033[0m')

    for epoch in tqdm(range(opt.epoch_count, opt.n_epochs + opt.n_epochs_decay + 1)):    # outer loop for different epochs; we save the model by <epoch_count>, <epoch_count>+<save_latest_freq>
        epoch_start_time = time.time()  # timer for entire epoch
        iter_data_time = time.time()    # timer for data loading per iteration
        epoch_iter = 0                  # the number of training iterations in current epoch, reset to 0 every epoch
        visualizer.reset()              # reset the visualizer: make sure it saves the results to HTML at least once every epoch

        # '''Validation'''
        # model.validate(dataloader_val)

        for i, data in enumerate(dataloader):  # inner loop within one epoch
            iter_start_time = time.time()  # timer for computation per iteration
            if total_iters % opt.print_freq == 0:
                t_data = iter_start_time - iter_data_time

            total_iters += opt.batch_size
            epoch_iter += opt.batch_size
            model.set_input(data)         # unpack data from dataset and apply preprocessing
            model.optimize_parameters()   # calculate loss functions, get gradients, update network weights

            if total_iters % opt.display_freq == 0:   # display images on visdom and save images to a HTML file
                save_result = total_iters % opt.update_html_freq == 0
                model.compute_visuals()
                visualizer.display_current_results(model.get_current_visuals(), epoch, save_result)

            if total_iters % opt.print_freq == 0:    # print training losses and save logging information to the disk
                losses = model.get_current_losses()
                t_comp = (time.time() - iter_start_time) / opt.batch_size
                visualizer.print_current_losses(epoch, epoch_iter, losses, t_comp, t_data)
                if opt.display_id > 0:
                    visualizer.plot_current_losses(epoch, float(epoch_iter) / dataset_size, losses)

            if total_iters % opt.save_latest_freq == 0:   # cache our latest model every <save_latest_freq> iterations
                print('saving the latest model (epoch %d, total_iters %d)' % (epoch, total_iters))
                save_suffix = 'iter_%d' % total_iters if opt.save_by_iter else 'latest'
                model.save_networks(save_suffix)

            iter_data_time = time.time()
        
        '''Validation'''
        model.validate(dataloader_val)
        
        model.update_learning_rate()    # update learning rates in the end of every epoch.

        if epoch % opt.save_epoch_freq == 0:              # cache our model every <save_epoch_freq> epochs
            print('saving the model at the end of epoch %d, iters %d' % (epoch, total_iters))
            model.save_networks('latest')
            model.save_networks(epoch)

        print('End of epoch %d / %d \t Time Taken: %d sec' % (epoch, opt.n_epochs + opt.n_epochs_decay, time.time() - epoch_start_time))