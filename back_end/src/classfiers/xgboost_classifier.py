import sklearn.model_selection
import xgboost as xgb
import pandas as pd
import numpy as np
from typing import Union, Dict
import os
import joblib

from ..data_process import evaluate_model
from ..config import label_encoder_len


class XGBoosterClassifier:
    """
    XGBoost Classifier
    """

    model: xgb.XGBClassifier = None

    def __init__(self):
        """
        初始化 XGBoost 分类器
        """

        self.model = xgb.XGBClassifier(
            booster="gbtree",
            verbosity=0,
            objective="multi:softprob",
            num_class=label_encoder_len,
            eta=0.1,  # 学习率，这里改为 0.1
            min_child_weight=3,
            max_depth=6,
            gamma=0.2,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=0.1,  # L1 正则化系数
            reg_lambda=0.1,  # L2 正则化系数
            random_state=42,  # 相当于之前的 seed
            n_jobs=-1,  # 使用所有可用的线程
            missing=np.inf,  # 缺失值处理方式
        )

    def fit(
        self, train_data: Union[pd.DataFrame, np.ndarray],
        train_label: Union[pd.Series, np.ndarray],
        eval_set: list = None,  # 添加评估集参数
        verbose: int = 1
    ):  # 添加 verbose 参数，控制输出频率
        """
        训练 XGBoost 分类器

        :param train_data: 训练数据
        :type train_data: Union[pd.DataFrame, np.ndarray]
        :param train_label: 训练标签
        :type train_label: Union[pd.Series, np.ndarray]
        :param eval_set: 评估集列表，格式为 [(X_eval, y_eval)]
        :type eval_set: list
        :param verbose: 每隔多少轮输出一次评估指标
        :type verbose: int
        """

        print("Training XGBoost Classifier...")
        self.model.fit(
            X=train_data,
            y=train_label,
            eval_set=eval_set,  # 传入评估集
            verbose=verbose  # 控制输出频率
        )
        print("XGBoost Classifier trained.")

    def store(self, model_path: str):
        """
        存储 XGBoost 分类器

        :param model_path: 模型保存路径
        :type model_path: str
        """

        print("Storing XGBoost Classifier model...")
        if not os.path.exists(os.path.dirname(model_path)):
            os.makedirs(os.path.dirname(model_path))

        path = os.path.join(model_path, "xgboost.joblib")

        joblib.dump(self.model, path)
        print()

    def load(self, model_path: str):
        """
        加载 XGBoost 分类器
        如果是输入文件夹, 那么默认的模型名称是 xgboost.joblib

        :param model_path: 模型加载路径
        :type model_path: str
        """

        print()

        if os.path.exists(model_path):
            if os.path.isdir(model_path):
                model_path = os.path.join(model_path, "xgboost.joblib")

        else:
            raise FileNotFoundError(model_path)

        self.model = joblib.load(model_path)

        if not isinstance(self.model, xgb.XGBClassifier):
            raise TypeError(
                "Loaded model is not an instance of XGBoostClassifier")
        print("XGBoost Classifier model loaded.")

    def predict_label(
            self, train_label: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        """
        使用 XGBoost 分类器进行预测

        :param train_label: 待预测数据
        :type train_label: Union[pd.DataFrame, np.ndarray]
        :return: 预测结果
        :rtype: np.ndarray
        """

        return self.model.predict(train_label)

    def predict_proba(
            self, train_data: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        """
        使用 XGBoost 分类器进行预测概率

        :param train_data: 待预测数据
        :type train_data: Union[pd.DataFrame, np.ndarray]
        :return: 预测概率
        :rtype: np.ndarray
        """

        return self.model.predict_proba(train_data)

    def cross_validate(
        self,
        x: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.Series, np.ndarray],
        label_encoder: Dict[str, int] = None,
    ):
        """
        进行 k 折交叉验证

        :param x: 特征数据
        :type x: Union[pd.DataFrame, np.ndarray]
        :param y: 标签数据
        :type y: Union[pd.Series, np.ndarray]
        :param label_encoder: Label encoder
        :type label_encoder: Dict[str, int]
        :return: 每折的得分
        :rtype: list
        """
        kf = sklearn.model_selection.StratifiedKFold(
            n_splits=5, shuffle=True, random_state=42)
        scores = []
        round_idx = 0
        for train_index, test_index in kf.split(x, y):
            x_train, x_test = x[train_index], x[test_index]
            y_train, y_test = y[train_index], y[test_index]
            if round_idx != 0:
                p_test_label = self.predict_label(x_test)
                p_test_proba = self.predict_proba(x_test)

                evaluate_model(
                    y_test,
                    p_test_label,
                    p_test_proba,
                    label_encoder,
                    f"D:/code_repository/mtd/image/xgboost_{round_idx}", )

            self.model.fit(
                X=x_train,
                y=y_train,
                # eval_set=[(x_test, y_test)],
                # verbose=1,
            )

            score = self.model.score(x_test, y_test)

            print(f'Round {round_idx} get score {score}')

            round_idx += 1
            scores.append(score)

        return scores
