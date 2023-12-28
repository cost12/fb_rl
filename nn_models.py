import torch
import torch.nn as nn
import torch.nn.functional as F

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


