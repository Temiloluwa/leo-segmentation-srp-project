# Entry point for the project
from utils import load_config
from data import Datagenerator
from model import LEO
from PIL import Image
from torchvision import transforms
from torch.autograd import variable
import argparse
import torch

parser = argparse  .ArgumentParser(description='Specify train or inference dataset')
parser.add_argument("-d", "--dataset", type=str, nargs=1, default="sample_data")
args = parser.parse_args()
dataset = args.dataset
print(dataset)

def get_in_sequence(data):
    dim_list = list(data.size())
    data = data.permute(2, 3, 0, 1)
    data = data.contiguous().view(dim_list[2], dim_list[3], -1)
    data = data.permute(2, 0, 1)
    data = data.unsqueeze(1) #because in the sample_data num_channels is missing
    data = data
    return data

def train_model(config):
    metatrain_dataloader = Datagenerator(dataset, config, data_type="train")
    epochs = config["hyperparameters"]["epochs"]

    for i in range(epochs):
        tr_data, tr_data_masks, val_data, val_masks = metatrain_dataloader.get_batch_data()

        print("tr_data shape: {},tr_data_masks shape: {}, val_data shape: {},val_masks shape: {}". \
              format(tr_data.size(), tr_data_masks.size(), val_data.size(), val_masks.size()))

        model = LEO(config)
        print(len(tr_data))
        for i in range(len(tr_data)):
            data_dict = {'tr_data_orig': tr_data[i], 'tr_data': get_in_sequence(tr_data[i]), 'tr_data_masks': get_in_sequence(tr_data_masks[i]),
                         'val_data_orig': val_data[i], 'val_data': get_in_sequence(val_data[i]), 'val_data_masks': get_in_sequence(val_masks[i])}

            #data = data.clone().detach().requires_grad_(True)#torch.tensor(data, requires_grad = True)
            latents, kl = model.forward_encoder(data_dict['tr_data'])
            tr_loss, adapted_segmentation_weights = model.leo_inner_loop(data_dict, latents)
            val_loss = model.finetuning_inner_loop(data_dict, tr_loss, adapted_segmentation_weights)
            batch_val_loss = torch.mean(val_loss)
            loss = torch.mean(batch_val_loss)
def predict_model(config):
    pass


def main():
    config = load_config()
    if config["train"]:
        train_model(config)
    else:
        predict_model(config)


if __name__ == "__main__":
    main()