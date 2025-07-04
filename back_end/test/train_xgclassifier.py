from src.classfiers import XGBoosterClassifier
from src.data_process import evaluate_model, read_labelled_csv, print_info

if __name__ == '__main__':
    train_data, train_label, test_data, test_label, label_encoder = read_labelled_csv(
        r"D:\code_repository\mtd\data\features",
        True,
    )

    print(f'finish reading labelled data')
    print_info(train_data, train_label, label_encoder, True)

    xgboost_classifier = XGBoosterClassifier()
    xgboost_classifier.cross_validate(train_data, train_label, label_encoder)
    xgboost_classifier.store(r"D:\code_repository\mtd\model")

    # xgboost_classifier.load(r"D:\code_repository\mtd\model")

    probabilities = xgboost_classifier.predict_proba(test_data)
    pridictions = xgboost_classifier.predict_label(test_data)

    evaluate_model(
        test_label,
        pridictions,
        probabilities,
        label_encoder,
        r"/result\xgboost"
    )
