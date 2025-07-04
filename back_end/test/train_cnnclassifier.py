from src.classfiers import CNNClassifier
from src.data_process import process_label_folders, evaluate_model
from src.config import label_encoder

if __name__ == "__main__":
    data_dir = r"D:\code_repository\mtd\data\image"

    # 读取数据
    train_images, train_labels = process_label_folders(data_dir)
    if train_images is not None and train_labels is not None and label_encoder is not None:
        # 初始化 CNNClassifier
        classifier = CNNClassifier(device="cuda")

        # 训练模型
        classifier.fit(
            train_data=train_images,
            train_label=train_labels,
            epochs=10,
            batch_size=16
        )

        classifier.store(r"D:\code_repository\mtd\model")

        # 预测
        predictions = classifier.predict_label(train_images)
        probabilities = classifier.predict_proba(train_images)
        evaluate_model(
            train_labels, predictions, probabilities, label_encoder, r"D:\code_repository\mtd\result\cnn"
        )
    else:
        raise ValueError('invalid arguments in image')
