import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
from typing import Union, Optional
import os

from ..config import label_encoder_len


class SimpleCNN(nn.Module):
    def __init__(self, num_classes: int):
        """
        初始化 CNN 模型
        输入的图像是 28x28 的灰度图像，输出是 num_classes 个类别的概率分布

        :param num_classes: 分类数量
        :type num_classes: int
        """
        super().__init__()
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, padding=1)
        self.relu1 = nn.ReLU()
        self.pool1 = nn.MaxPool2d(2)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.relu2 = nn.ReLU()
        self.pool2 = nn.MaxPool2d(2)
        self.fc1 = nn.Linear(32 * 7 * 7, 128)
        self.relu3 = nn.ReLU()
        self.fc2 = nn.Linear(128, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.pool1(self.relu1(self.conv1(x)))
        x = self.pool2(self.relu2(self.conv2(x)))
        x = x.view(-1, 32 * 7 * 7)
        x = self.relu3(self.fc1(x))
        x = self.fc2(x)
        return x


class CNNClassifier:
    """
    CNN 分类器
    """

    def __init__(self, device: str = "cuda"):
        """
        初始化 CNN 分类器

        :param device: 计算设备，可选 'cpu' 或 'cuda'
        :type device: str
        """
        self.device = torch.device(device)
        self.model = SimpleCNN(num_classes=label_encoder_len).to(self.device)
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.scheduler = optim.lr_scheduler.StepLR(
            self.optimizer, step_size=5, gamma=0.1
        )

    def _convert_data(
        self,
        data: np.ndarray,
        label: Optional[np.ndarray] = None,
    ) -> Union[torch.Tensor, TensorDataset]:
        """
        将输入数据转换为 PyTorch 张量或数据集

        :param data: 输入数据，形状应为 (num_images, 28, 28) 的 numpy.ndarray
        :type data: np.ndarray
        :param label: 输入标签，可选，形状应为 (num_images,) 的 numpy.ndarray
        :type label: Optional[np.ndarray]
        :return: 转换后的张量或数据集，如果有标签则返回 TensorDataset，否则返回张量
        :rtype: Union[torch.Tensor, TensorDataset]
        """
        data = torch.tensor(
            data, dtype=torch.float32).unsqueeze(1).to(
            self.device)
        if label is not None:
            label = torch.tensor(label, dtype=torch.long).to(self.device)
            return TensorDataset(data, label)
        return data

    def fit(
        self,
        train_data: np.ndarray,
        train_label: np.ndarray,
        epochs: int = 20,
        batch_size: int = 32,
        val_data: Optional[np.ndarray] = None,
        val_label: Optional[np.ndarray] = None,
    ) -> None:
        """
        训练 CNN 分类器

        :param train_data: 训练数据，形状应为 (num_images, 28, 28) 的 numpy.ndarray
        :type train_data: np.ndarray
        :param train_label: 训练标签，形状应为 (num_images,) 的 numpy.ndarray
        :type train_label: np.ndarray
        :param epochs: 训练轮数
        :type epochs: int
        :param batch_size: 批次大小
        :type batch_size: int
        :param val_data: 验证数据，可选，形状应为 (num_images, 28, 28) 的 numpy.ndarray
        :type val_data: Optional[np.ndarray]
        :param val_label: 验证标签，可选，形状应为 (num_images,) 的 numpy.ndarray
        :type val_label: Optional[np.ndarray]
        """
        print("Training CNN Classifier...")
        train_dataset = self._convert_data(train_data, train_label)
        train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True
        )

        val_loader = None
        if val_data is not None and val_label is not None:
            val_dataset = self._convert_data(val_data, val_label)
            val_loader = DataLoader(
                val_dataset,
                batch_size=batch_size,
                shuffle=False
            )

        for epoch in range(epochs):
            self.model.train()
            running_loss = 0.0
            for inputs, labels in train_loader:
                self.optimizer.zero_grad()
                outputs = self.model(inputs)
                loss = self.criterion(outputs, labels)
                loss.backward()
                self.optimizer.step()
                running_loss += loss.item()

            self.scheduler.step()
            train_loss = running_loss / len(train_loader)

            if val_loader is not None:
                val_loss = self.evaluate(val_loader)
                print(
                   
                )
            else:
                print()

        print("CNN Classifier trained.")

    def evaluate(self, data_loader: DataLoader) -> float:
        """
        评估模型在给定数据集上的损失

        :param data_loader: 数据加载器
        :type data_loader: DataLoader
        :return: 平均损失
        :rtype: float
        """
        self.model.eval()
        running_loss = 0.0
        with torch.no_grad():
            for inputs, labels in data_loader:
                outputs = self.model(inputs)
                loss = self.criterion(outputs, labels)
                running_loss += loss.item()
        return running_loss / len(data_loader)

    def store(self, folder_path: str) -> None:
        """
        存储 CNN 分类器及其相关信息

        :param folder_path: 文件夹路径，模型文件将保存于此
        """
        model_path = os.path.join(folder_path, "cnn.pth")
        try:
            state_dict = {
                "model_state_dict": self.model.state_dict(),
                "optimizer_state_dict": self.optimizer.state_dict(),
                "scheduler_state_dict": self.scheduler.state_dict()
            }
            torch.save(state_dict, model_path)
            print()
        except Exception as e:
            print()

    def load(self, src_path: str) -> None:
        """
        加载 CNN 分类器及其相关信息

        :param src_path: 文件夹路径，模型文件将从这里加载
        """
        if os.path.isdir(src_path):
            src_path = os.path.join(src_path, "cnn.pth")

        try:
            state_dict = torch.load(src_path, map_location=self.device)
            saved_num_classes = state_dict["model_state_dict"]["fc2.weight"].shape[0]
            current_num_classes = label_encoder_len
            if saved_num_classes != current_num_classes:
                print(
                    
                )
                # 过滤掉不匹配的层参数
                model_state_dict = self.model.state_dict()
                pretrained_dict = {k: v for k, v in state_dict["model_state_dict"].items()
                    if k in model_state_dict and v.shape == model_state_dict[k].shape}
                model_state_dict.update(pretrained_dict)
                self.model.load_state_dict(model_state_dict)
            else:
                self.model.load_state_dict(state_dict["model_state_dict"])

            self.optimizer.load_state_dict(state_dict["optimizer_state_dict"])
            self.scheduler.load_state_dict(state_dict["scheduler_state_dict"])
            self.model.eval()
            print("CNN Classifier model loaded.")
        except Exception as e:
            print()

    def predict_label(
            self, test_data: np.ndarray) -> np.ndarray:
        """
        使用 CNN 分类器进行预测

        :param test_data: 待预测数据，形状应为 (num_images, 28, 28) 的 numpy.ndarray
        :type test_data: np.ndarray
        :return: 预测结果
        :rtype: np.ndarray
        """
        test_data = self._convert_data(test_data)
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(test_data)
            _, predicted = torch.max(outputs.data, 1)
        return predicted.cpu().numpy()

    def predict_proba(
            self, test_data: np.ndarray) -> np.ndarray:
        """
        使用 CNN 分类器进行预测概率

        :param test_data: 待预测数据，形状应为 (num_images, 28, 28) 的 numpy.ndarray
        :type test_data: np.ndarray
        :return: 预测概率
        :rtype: np.ndarray
        """
        test_data = self._convert_data(test_data)
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(test_data)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
        return probabilities.cpu().numpy()
