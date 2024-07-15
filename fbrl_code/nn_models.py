import torch
import torch.nn as nn
import torch.nn.functional as F

"""
The goal for the NN is to take in a state and output predictions for the Q-values of each move
"""

class SimpleNN(nn.Module):
    
    def __init__(self, in_dim, out_dim, num_hidden_layers, layer_size):
        super().__init__()

        self.in_dim = in_dim
        self.out_dim = out_dim        
        self.layer_size = layer_size
        self.layer_list = nn.ModuleList()
        self.layer_list.append(nn.Linear(self.in_dim, self.layer_size))
        self.num_hidden_layers = num_hidden_layers
        for _ in range(0,self.num_hidden_layers):
            self.layer_list.append(nn.Linear(self.layer_size, self.layer_size))
        self.layer_list.append(nn.Linear(self.layer_size, self.out_dim))
        
    def forward(self, x):
        x = x.view(-1, self.in_dim)
        #print(type(x[0][0].item()))
        #print(x.shape)
        for i in range(self.num_hidden_layers+1):
            x = F.tanh(self.layer_list[i](x))
            #print(x.shape)
        out = self.layer_list[self.num_hidden_layers+1](x)
        return out

    def save(self, filename):
        torch.save(self.state_dict(), filename)

    def load(self, filename):
        self.load_state_dict(torch.load(filename))

class ComplexNN(nn.Module):
    
    def __init__(self, in_dim, out_dim, num_hidden, layer_size, dropout):
        super().__init__()

        self.in_dim = in_dim
        self.out_dim = out_dim
        self.fc_layer_neurons = layer_size
        self.num_hidden_layers = num_hidden
        self.dropout = dropout

        self.first_batch = nn.BatchNorm1d(self.in_dim)
        self.layer_list = nn.ModuleList()
        self.layer_dropout = nn.ModuleList()
        self.batch_norm_layer = nn.ModuleList()
        self.layer_list.append(nn.Linear(self.in_dim, self.fc_layer_neurons))
        self.batch_norm_layer.append(nn.BatchNorm1d(self.fc_layer_neurons))
        self.layer_dropout.append(nn.Dropout1d(self.dropout))
        for i in range(0,num_hidden):
            self.layer_list.append(nn.Linear(self.fc_layer_neurons,self.fc_layer_neurons))
            self.batch_norm_layer.append(nn.BatchNorm1d(self.fc_layer_neurons))
            self.layer_dropout.append(nn.Dropout1d(self.dropout))

        self.lin_out = nn.Linear(self.fc_layer_neurons, self.out_dim)

    def forward(self, x):
        x = x.view(-1, self.in_dim)
        x = self.first_batch(x)
        for i in range(self.num_hidden_layers+1):
            self.layer_dropout[i](x)
            x = self.layer_list[i](x)
            x = F.tanh(self.batch_norm_layer[i](x))
        x = self.lin_out(x)
        return x

    def save(self, filename):
        torch.save(self.state_dict(), filename)

    def load(self, filename):
        self.load_state_dict(torch.load(filename))

class CNN(nn.Module):
    """
    The input state will be the board (3x10 usually) and the output state will be the moves (7 options usually)
    """
    def __init__(self, in_dim=(1,3,10), out_dim=7, num_cvn_layers=2, num_filters=3, num_hidden=2, layer_size=256, dropout=0.5,*
                 ,kernel_size=(3,3),stride=1,padding=0,channels=1,total_weights=0):
        super().__init__()

        self.in_dim = in_dim # 2d
        self.out_dim = out_dim
        self.num_cvn_layers = num_cvn_layers
        self.num_filters = num_filters
        self.fc_layer_neurons = layer_size
        self.num_hidden_layers = num_hidden
        self.dropout = dropout

        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = padding
        # channel is like filter, but channels is for the data coming in and filters is for after it passes through
        self.channels = channels
        self.total_weights = total_weights

        self.dim_h = (self.in_dim[1] - self.kernel_size[0]) / self.stride + 1 # resulting height
        self.dim_w = (self.in_dim[2] - self.kernel_size[1]) / self.stride + 1 # resulting width

        self.cvn_list = nn.ModuleList()
        self.cvn_dropout = nn.ModuleList()
        self.batch_norm_cvn = nn.ModuleList()

        self.norm1 = nn.BatchNorm2d(self.channels)
        conv1 = nn.Conv2d(self.channels, self.num_filters, self.kernel_size, stride=self.stride, padding=self.padding)
        bn1 = nn.BatchNorm2d(self.num_filters)
        self.total_weights += self.num_filters * self.kernel_size[0] * self.kernel_size[1] * self.channels

        self.cvn_list.append(conv1)
        self.batch_norm_cvn.append(bn1)
        self.channels = num_filters
        self.cvn_dropout.append(nn.Dropout2d(self.dropout))

        for _ in range(1,num_cvn_layers):
            self.dim_h = (self.dim_h - self.kernel_size[0]) / self.stride + 1
            self.dim_w = (self.dim_w - self.kernel_size[1]) / self.stride + 1
            convn = nn.Conv2d(self.channels, self.num_filters, self.kernel_size, stride=self.stride, padding=self.padding)
            bn = nn.BatchNorm2d(self.num_filters)
            self.cvn_list.append(convn)
            self.batch_norm_cvn.append(bn)
            self.total_weights += self.num_filters * self.kernel_size[0] * self.kernel_size[1] * self.channels
            self.cvn_dropout.append(nn.Dropout2d(self.dropout))
        # end of convolution

        self.fc_inputs = int(self.num_filters * self.dim_h * self.dim_w)

        # start of fully connected
        self.first_batch = nn.BatchNorm1d(self.fc_inputs)
        self.layer_list = nn.ModuleList()
        self.layer_dropout = nn.ModuleList()
        self.batch_norm_layer = nn.ModuleList()
        self.layer_list.append(nn.Linear(self.fc_inputs, self.fc_layer_neurons))
        self.batch_norm_layer.append(nn.BatchNorm1d(self.fc_layer_neurons))
        self.total_weights += self.fc_inputs * self.fc_layer_neurons
        self.layer_dropout.append(nn.Dropout1d(self.dropout))
        for _ in range(0,num_hidden):
            self.layer_list.append(nn.Linear(self.fc_layer_neurons,self.fc_layer_neurons))
            self.batch_norm_layer.append(nn.BatchNorm1d(self.fc_layer_neurons))
            self.total_weights += self.fc_layer_neurons * self.fc_layer_neurons
            self.layer_dropout.append(nn.Dropout1d(self.dropout))

        self.lin_out = nn.Linear(self.fc_layer_neurons, self.out_dim)
        self.total_weights += self.fc_layer_neurons * self.out_dim

    def forward(self, x):
        x = self.norm1(x)
        for i in range(self.num_cvn_layers):
            self.cvn_dropout[i](x)
            x = F.relu(self.batch_norm_cvn[i](self.cvn_list[i](x)))

        # flatten convolutional layer into vector
        x = self.first_batch(x.view(x.size(0), -1))
        for i in range(self.num_hidden_layers):
            self.layer_dropout[i](x)
            x = F.relu(self.batch_norm_layer[i](self.layer_list[i](x)))
        x = self.lin_out(x)
        return x

    def save(self, filename):
        torch.save(self.state_dict(), filename)

    def load(self, filename):
        self.load_state_dict(torch.load(filename))

class HybridNN(nn.Module):
    """
    The input state will be the board (3x10 usually) and the output state will be the moves (7 options usually)
    """
    def __init__(self, in_dim=(1,3,10), out_dim=7, add_dim=0, num_cvn_layers=2, num_filters=3, num_hidden=2, layer_size=256, dropout=0.5,*
                 ,kernel_size=(3,3),stride=1,padding=0,channels=1,total_weights=0):
        super().__init__()

        self.in_dim = in_dim # 2d
        self.out_dim = out_dim
        self.add_dim = add_dim
        self.num_cvn_layers = num_cvn_layers
        self.num_filters = num_filters
        self.fc_layer_neurons = layer_size
        self.num_hidden_layers = num_hidden
        self.dropout = dropout

        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = padding
        # channel is like filter, but channels is for the data coming in and filters is for after it passes through
        self.channels = channels
        self.total_weights = total_weights

        self.dim_h = (self.in_dim[1] - self.kernel_size[0]) / self.stride + 1 # resulting height
        self.dim_w = (self.in_dim[2] - self.kernel_size[1]) / self.stride + 1 # resulting width

        self.cvn_list = nn.ModuleList()
        self.cvn_dropout = nn.ModuleList()
        self.batch_norm_cvn = nn.ModuleList()

        self.norm1 = nn.BatchNorm2d(self.channels)
        conv1 = nn.Conv2d(self.channels, self.num_filters, self.kernel_size, stride=self.stride, padding=self.padding)
        bn1 = nn.BatchNorm2d(self.num_filters)
        self.total_weights += self.num_filters * self.kernel_size[0] * self.kernel_size[1] * self.channels

        self.cvn_list.append(conv1)
        self.batch_norm_cvn.append(bn1)
        self.channels = num_filters
        self.cvn_dropout.append(nn.Dropout2d(self.dropout))

        for _ in range(1,num_cvn_layers):
            self.dim_h = (self.dim_h - self.kernel_size[0]) / self.stride + 1
            self.dim_w = (self.dim_w - self.kernel_size[1]) / self.stride + 1
            convn = nn.Conv2d(self.channels, self.num_filters, self.kernel_size, stride=self.stride, padding=self.padding)
            bn = nn.BatchNorm2d(self.num_filters)
            self.cvn_list.append(convn)
            self.batch_norm_cvn.append(bn)
            self.total_weights += self.num_filters * self.kernel_size[0] * self.kernel_size[1] * self.channels
            self.cvn_dropout.append(nn.Dropout2d(self.dropout))
        # end of convolution

        self.fc_inputs = int(self.num_filters * self.dim_h * self.dim_w + self.add_dim)

        # start of fully connected
        self.first_batch = nn.BatchNorm1d(self.fc_inputs)
        self.layer_list = nn.ModuleList()
        self.layer_dropout = nn.ModuleList()
        self.batch_norm_layer = nn.ModuleList()
        self.layer_list.append(nn.Linear(self.fc_inputs, self.fc_layer_neurons))
        self.batch_norm_layer.append(nn.BatchNorm1d(self.fc_layer_neurons))
        self.total_weights += self.fc_inputs * self.fc_layer_neurons
        self.layer_dropout.append(nn.Dropout1d(self.dropout))
        for _ in range(0,num_hidden):
            self.layer_list.append(nn.Linear(self.fc_layer_neurons,self.fc_layer_neurons))
            self.batch_norm_layer.append(nn.BatchNorm1d(self.fc_layer_neurons))
            self.total_weights += self.fc_layer_neurons * self.fc_layer_neurons
            self.layer_dropout.append(nn.Dropout1d(self.dropout))

        self.lin_out = nn.Linear(self.fc_layer_neurons, self.out_dim)
        self.total_weights += self.fc_layer_neurons * self.out_dim

    def forward(self, x, add):
        x = self.norm1(x)
        for i in range(self.num_cvn_layers):
            self.cvn_dropout[i](x)
            x = F.relu(self.batch_norm_cvn[i](self.cvn_list[i](x)))

        x = x.view(x.size(0), -1)
        x = torch.cat((x,add),1)
        x = self.first_batch(x)
        for i in range(self.num_hidden_layers):
            self.layer_dropout[i](x)
            x = F.relu(self.batch_norm_layer[i](self.layer_list[i](x)))
        x = self.lin_out(x)
        return x

    def save(self, filename):
        torch.save(self.state_dict(), filename)

    def load(self, filename):
        self.load_state_dict(torch.load(filename))

class CNN_2(nn.Module):
    
    def __init__(self, in_dim, out_dim, num_cvn_layers, num_filters, layer_size, num_hidden, dropout):
        super().__init__()

        self.in_dim = in_dim
        self.out_dim = out_dim

        self.num_cvn_layers = num_cvn_layers
        self.fc_layer_neurons = layer_size
        self.num_hidden_layers = num_hidden
        self.dropout = dropout

        self.filters = num_filters
        self.kernel_size = (4,4)
        self.stride = 1
        self.padding = 0
        self.channels = 3
        self.total_weights = 0

        self.dim_h = (self.in_dim[1] - self.kernel_size[0]) / self.stride + 1
        self.dim_w = (self.in_dim[2] - self.kernel_size[1]) / self.stride + 1

        self.cvn_list = nn.ModuleList()
        self.cvn_dropout = nn.ModuleList()
        self.batch_norm_cvn = nn.ModuleList()
        conv1 = nn.Conv2d(self.channels, self.filters, self.kernel_size, stride=self.stride, padding=self.padding)
        bn1 = nn.BatchNorm2d(self.filters)
        self.total_weights += self.filters * self.kernel_size[0] * self.kernel_size[1] * self.channels
        print(f"{self.filters} * {self.kernel_size[0]} * {self.kernel_size[1]} * {self.channels}")
        self.cvn_list.append(conv1)
        self.batch_norm_cvn.append(bn1)
        self.channels = num_filters
        self.cvn_dropout.append(nn.Dropout2d(self.dropout))
        for i in range(1,num_cvn_layers):
            self.dim_h = (self.dim_h - self.kernel_size[0]) / self.stride + 1
            self.dim_w = (self.dim_w - self.kernel_size[1]) / self.stride + 1
            convn = nn.Conv2d(self.channels, self.filters, self.kernel_size, stride=self.stride, padding=self.padding)
            bn = nn.BatchNorm2d(self.filters)
            self.cvn_list.append(convn)
            self.batch_norm_cvn.append(bn)
            self.total_weights += self.filters * self.kernel_size[0] * self.kernel_size[1] * self.channels
            print(f" + {self.filters} * {self.kernel_size[0]} * {self.kernel_size[1]} * {self.channels}")
            self.cvn_dropout.append(nn.Dropout2d(self.dropout))

        self.fc_inputs = int(self.filters * self.dim_h * self.dim_w)
        print(f"inputs: {self.filters} * {self.dim_h} * {self.dim_w}")

        self.layer_list = nn.ModuleList()
        self.layer_dropout = nn.ModuleList()
        self.batch_norm_layer = nn.ModuleList()
        self.layer_list.append(nn.Linear(self.fc_inputs, self.fc_layer_neurons))
        self.batch_norm_layer.append(nn.BatchNorm1d(self.fc_layer_neurons))
        self.total_weights += self.fc_inputs * self.fc_layer_neurons
        print(f"{self.fc_inputs} * {self.fc_layer_neurons}")
        self.layer_dropout.append(nn.Dropout1d(self.dropout))
        for i in range(1,num_hidden):
            self.layer_list.append(nn.Linear(self.fc_layer_neurons,self.fc_layer_neurons))
            self.batch_norm_layer.append(nn.BatchNorm1d(self.fc_layer_neurons))
            self.total_weights += self.fc_layer_neurons * self.fc_layer_neurons
            print(f" + {self.fc_layer_neurons} * {self.fc_layer_neurons}")
            self.layer_dropout.append(nn.Dropout1d(self.dropout))

        self.lin_out = nn.Linear(self.fc_layer_neurons, self.out_dim)
        self.total_weights += self.fc_layer_neurons * self.out_dim
        print(f" + {self.fc_inputs} * {self.out_dim}")
        print(f"Total weights: {self.total_weights}")


    def forward(self, x):
        for i in range(self.num_cvn_layers):
            self.cvn_dropout[i](x)
            x = F.relu(self.batch_norm_cvn[i](self.cvn_list[i](x)))

        # flatten convolutional layer into vector
        x = x.view(x.size(0), -1)
        for i in range(self.num_hidden_layers):
            self.layer_dropout[i](x)
            x = F.relu(self.batch_norm_layer[i](self.layer_list[i](x)))
        x = self.lin_out(x)
        return x