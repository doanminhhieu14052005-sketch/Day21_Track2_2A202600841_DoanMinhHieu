import mlflow
import mlflow.sklearn
import pandas as pd
import yaml
import json
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score

EVAL_THRESHOLD = 0.70


def train(
    params: dict,
    data_path: str = "data/train_phase1.csv",
    eval_path: str = "data/eval.csv",
) -> float:
    """
    Huan luyen mo hinh va ghi nhan ket qua vao MLflow.

    Tham so:
        params     : dict chua cac sieu tham so cho RandomForestClassifier.
        data_path  : duong dan den file du lieu huan luyen.
        eval_path  : duong dan den file du lieu danh gia.

    Tra ve:
        accuracy (float): do chinh xac tren tap danh gia.
    """

    # 1. Doc du lieu huan luyen va danh gia
    #    data_path co the la mot duong dan (str) hoac danh sach nhieu file;
    #    neu la danh sach, gop tat ca lai de tang luong du lieu huan luyen.
    if isinstance(data_path, (list, tuple)):
        df_train = pd.concat([pd.read_csv(p) for p in data_path], ignore_index=True)
    else:
        df_train = pd.read_csv(data_path)
    df_eval = pd.read_csv(eval_path)

    # 2. Tach dac trung (X) va nhan (y)
    X_train = df_train.drop(columns=["target"])
    y_train = df_train["target"]
    X_eval = df_eval.drop(columns=["target"])
    y_eval = df_eval["target"]

    with mlflow.start_run():

        # 3. Ghi nhan cac sieu tham so
        mlflow.log_params(params)

        # 4. Khoi tao va huan luyen RandomForestClassifier
        model = RandomForestClassifier(**params, random_state=42)
        model.fit(X_train, y_train)

        # 5. Du doan tren tap danh gia va tinh chi so
        preds = model.predict(X_eval)
        acc = accuracy_score(y_eval, preds)
        f1 = f1_score(y_eval, preds, average="weighted")

        # 6. Ghi nhan chi so vao MLflow
        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("f1_score", f1)
        mlflow.sklearn.log_model(model, "model")

        # 7. In ket qua ra man hinh
        print(f"Accuracy: {acc:.4f} | F1: {f1:.4f}")

        # 8. Luu metrics ra file outputs/metrics.json
        os.makedirs("outputs", exist_ok=True)
        with open("outputs/metrics.json", "w") as f:
            json.dump({"accuracy": acc, "f1_score": f1}, f)

        # 9. Luu mo hinh ra file models/model.pkl
        os.makedirs("models", exist_ok=True)
        joblib.dump(model, "models/model.pkl")

    # 10. Tra ve acc
    return acc


if __name__ == "__main__":
    with open("params.yaml") as f:
        params = yaml.safe_load(f)
    # Huan luyen tren ca hai phase de co du du lieu vuot nguong accuracy.
    train(params, data_path=["data/train_phase1.csv", "data/train_phase2.csv"])
