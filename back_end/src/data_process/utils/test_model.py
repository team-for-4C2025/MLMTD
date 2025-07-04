import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import torch
import os

from typing import Union, Dict
from itertools import cycle
from sklearn.calibration import label_binarize
from sklearn.metrics import (
    accuracy_score,
    auc,
    recall_score,
    precision_score,
    f1_score,
    confusion_matrix,
    roc_curve,
)


def evaluate_model(
    test_labels: Union[pd.Series, np.ndarray, torch.Tensor],
    predictions: Union[pd.Series, np.ndarray, torch.Tensor],
    probability: np.ndarray,
    label_encoder: Dict[str, int],
    save_path: str,
):
    """
    对模型进行评估

    :param test_labels: 测试数据对应的标签
    :type test_labels: Union[pd.Series, np.ndarray, torch.Tensor]
    :param predictions: 模型预测的标签
    :type predictions: Union[pd.Series, np.ndarray, torch.Tensor]
    :param probability: 模型预测的概率
    :type probability: np.ndarray
    :param label_encoder: 标签编码器, 用于将整数标签转换为字符串标签
    :type label_encoder: Dict[str, int]
    :param save_path: 保存图像的文件夹
    :type save_path: str
    :return: None
    """
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    print("Evaluating model...")
    calculate_score(test_labels, predictions)
    draw_roc_curve(
        test_labels, probability, label_encoder, os.path.join(
            save_path, "curve.png")
    )
    draw_confusion_matrix(
        test_labels,
        predictions,
        label_encoder,
        os.path.join(save_path, "confusion.png"),
    )


def check_label(
    label: Union[pd.Series, np.ndarray, torch.Tensor],
    predictions: Union[pd.Series, np.ndarray, torch.Tensor],
) -> None:
    """
    检查标签和预测值的类型是否一致

    :param label:
    :type label: Union[pd.Series, np.ndarray, torch.Tensor]
    :param predictions:
    :type predictions: Union[pd.Series, np.ndarray, torch.Tensor]
    :return: None
    :rtype: None
    :raises ValueError: 如果标签和预测值的类型不一致，则抛出 ValueError 异常
    """
    if label.shape[0] != predictions.shape[0]:
        raise ValueError(
            f"The shape of label {label.shape} and predictions { predictions.shape} is not equal."
        )


def calculate_score(
    test_labels: Union[pd.Series, np.ndarray, torch.Tensor],
    predictions: Union[pd.Series, np.ndarray, torch.Tensor],
):
    """
    计算模型的准确率、召回率、精准率和 F1 分数

    :param test_labels: 测试数据对应的标签
    :type test_labels: Union[pd.Series, np.ndarray, torch.Tensor]
    :param predictions: 模型预测的标签
    :type predictions: Union[pd.Series, np.ndarray, torch.Tensor]
    :return: 准确率、召回率、精准率和 F1 分数
    :rtype: tuple
    """
    check_label(test_labels, predictions)

    print("Calculating scores...")
    accuracy = accuracy_score(test_labels, predictions)
    recall = recall_score(test_labels, predictions, average="weighted")
    precision = precision_score(test_labels, predictions, average="weighted")
    f1 = f1_score(test_labels, predictions, average="weighted")

    print()
    print()
    print()
    print()


def draw_confusion_matrix(
    test_labels: Union[pd.Series, np.ndarray, torch.Tensor],
    predictions: Union[pd.Series, np.ndarray, torch.Tensor],
    label_encoder: Dict[str, int],
    save_path: str,
):
    """
    绘制混淆矩阵

    :param test_labels: 测试数据对应的标签, 类型可以是 pandas 的 Series、NumPy 数组或者 PyTorch 的 Tensor
    :type test_labels: Union[pd.Series, np.ndarray, torch.Tensor]
    :param predictions: 模型预测的标签, 类型可以是 pandas 的 Series、NumPy 数组或者 PyTorch 的 Tensor
    :type predictions: Union[pd.Series, np.ndarray, torch.Tensor]
    :param label_encoder: 标签编码器, 用于将整数标签转换为字符串标签
    :type predictions: Union[pd.Series, np.ndarray, torch.Tensor]
    :param save_path: 保存混淆矩阵的路径
    :type save_path: str
    """
    check_label(test_labels, predictions)

    print("Drawing confusion matrix...")

    # 转换为 numpy 数组
    if isinstance(test_labels, pd.Series):
        test_labels = test_labels.values
    elif isinstance(test_labels, torch.Tensor):
        test_labels = test_labels.numpy()
    if isinstance(predictions, pd.Series):
        predictions = predictions.values
    elif isinstance(predictions, torch.Tensor):
        predictions = predictions.numpy()

    # 计算混淆矩阵
    cm = confusion_matrix(test_labels, predictions)
    classes = np.unique(test_labels)
    num_classes = len(classes)

    # 将整数标签转换为字符串标签
    str_classes = list(label_encoder.keys())

    # 设置颜色映射
    cmap = plt.get_cmap("Blues")

    fig, ax = plt.subplots(figsize=(20, 20))
    im = ax.imshow(cm, interpolation="nearest", cmap=cmap)
    ax.figure.colorbar(im, ax=ax)

    # 设置坐标轴标签
    ax.set(
        xticks=np.arange(num_classes),
        yticks=np.arange(num_classes),
        xticklabels=str_classes,
        yticklabels=str_classes,
        title="Confusion matrix",
        ylabel="True label",
        xlabel="Predicted label",
    )

    # 旋转 x 轴标签
    plt.setp(
        ax.get_xticklabels(),
        rotation=45,
        ha="right",
        rotation_mode="anchor")

    # 显示矩阵中的数值
    thresh = cm.max() / 2.0
    for i in range(num_classes):
        for j in range(num_classes):
            ax.text(
                j,
                i,
                format(cm[i, j], "d"),
                ha="center",
                va="center",
                color="white" if cm[i, j] > thresh else "black",
            )
    try:
        plt.savefig(save_path)
    except AttributeError:
        print("Error: self.model_type does not have a 'value' attribute.")
    except Exception as e:
        print()


def draw_roc_curve(
    test_labels: Union[pd.Series, np.ndarray, torch.Tensor],
    probability: np.ndarray,
    label_encoder: Dict[str, int],
    save_path: str,
):
    """
    绘制多类别 ROC 曲线
    保存至某路径

    :test_labels: 测试数据对应的标签, 类型可以是 pandas 的 Series、NumPy 数组或者 PyTorch 的 Tensor
    :type test_labels: Union[pd.Series, np.ndarray, torch.Tensor]
    :param probability: 模型预测的概率, 类型为 NumPy 数组
    :type probability: np.ndarray
    :param label_encoder: 标签编码器, 用于将整数标签转换为字符串标签
    :type label_encoder: Dict[str, int]
    :param save_path: 保存 ROC 曲线的路径
    :type save_path: str
    """
    print("Drawing ROC curve...")

    # 转换 test_label 为 numpy 数组
    if isinstance(test_labels, pd.Series):
        test_labels = test_labels.values
    elif isinstance(test_labels, torch.Tensor):
        test_labels = test_labels.numpy()

    unique_labels = np.unique(test_labels)
    label_num = len(unique_labels)

    if label_num == 2:  # 二分类问题
        fpr, tpr, _ = roc_curve(test_labels, probability[:, 1])
        roc_auc = auc(fpr, tpr)

        plt.figure(figsize=(20, 20))
        plt.plot(
            fpr,
            tpr,
            color="darkorange",
            lw=2,
            label=f"ROC curve (area = {roc_auc:0.2f})",
        )
        plt.plot([0, 1], [0, 1], "k--", lw=2)
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.title("Receiver operating characteristic for binary class")
        plt.legend(loc="lower right")
    else:  # 多分类问题
        test_label_bin = label_binarize(
            test_labels, classes=np.arange(label_num))

        print(
            
        )

        # 计算每个类别的 ROC 曲线和 AUC
        fpr = dict()
        tpr = dict()
        roc_auc = dict()
        for i in range(label_num):
            fpr[i], tpr[i], _ = roc_curve(
                test_label_bin[:, i], probability[:, i])
            roc_auc[i] = auc(fpr[i], tpr[i])

        str_classes = list(label_encoder.keys())

        # 绘制每个类别的 ROC 曲线
        plt.figure(figsize=(20, 20))
        colors = cycle(["aqua", "darkorange", "cornflowerblue"])
        for i, color in zip(range(label_num), colors):
            plt.plot(
                fpr[i],
                tpr[i],
                color=color,
                lw=2,
                
            )

        plt.plot([0, 1], [0, 1], "k--", lw=2)
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.title("Receiver operating characteristic for multi-class")
        plt.legend(loc="lower right")

    plt.savefig(save_path)
