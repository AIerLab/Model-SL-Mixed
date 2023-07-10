import pickle
from time import sleep

import torch
from model import AbstractModel
from queue import Queue


class SplitServerLayer(AbstractModel):
    def __init__(self, model_dir: str, in_queue: Queue, out_queue: Queue, device=None, first_layer=False, last_layer=False):
        super().__init__(model_dir)
        # get all model layers
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.first_layer = first_layer
        self.last_layer = last_layer

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if not self.first_layer:
            while not self.out_queue.empty():
                sleep(0.1)
            # pickle the tensor data
            serialized_data = pickle.dumps(x)
            # Send the result to the server
            data = {"byte_data": serialized_data, "stage": "forward"}
            self.out_queue.put(data)

        while self.in_queue.empty():
            sleep(0.1)
        data = self.in_queue.get()
        # print(repr(serialized_data))
        x = pickle.loads(data["byte_data"])

        if type(x) is str:
            while self.in_queue.empty():
                sleep(0.1)
            data = self.in_queue.get()
            # print(repr(serialized_data))
            x = pickle.loads(data["byte_data"])
            x.to(self.device)

        return x

    def backward(self, grad: torch.Tensor):
        if not self.last_layer:
            while not self.out_queue.empty():
                sleep(0.1)
            # pickle the tensor data
            serialized_data = pickle.dumps(grad)
            # Send the result to the server
            data = {"byte_data": serialized_data, "stage": "backward"}
            self.out_queue.put(data)

        while self.in_queue.empty():
            sleep(0.1)
        data = self.in_queue.get()
        # print(repr(serialized_data))
        grad = pickle.loads(data["byte_data"])
        grad = grad.to(self.device)

        return grad
