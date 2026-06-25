"""
Script chay 3 thi nghiem voi cac sieu tham so khac nhau.
Ket qua duoc ghi vao MLflow de so sanh.
"""
import os
import yaml

os.environ["MLFLOW_TRACKING_URI"] = "sqlite:///mlflow.db"
os.environ["MLFLOW_ARTIFACT_ROOT"] = "./mlartifacts"

from src.train import train

experiments = [
    {"n_estimators": 100, "max_depth": 5, "min_samples_split": 2},
    {"n_estimators": 50,  "max_depth": 3, "min_samples_split": 2},
    {"n_estimators": 200, "max_depth": 10, "min_samples_split": 5},
    {"n_estimators": 150, "max_depth": None, "min_samples_split": 2},
    {"n_estimators": 300, "max_depth": 15, "min_samples_split": 3},
]

print("=" * 60)
print("CHAY 5 THI NGHIEM VOI CAC SIEU THAM SO KHAC NHAU")
print("=" * 60)

results = []
for i, params in enumerate(experiments, 1):
    print(f"\n--- Thi nghiem {i}/{len(experiments)} ---")
    print(f"Params: {params}")
    acc = train(params)
    results.append((params, acc))
    print()

print("\n" + "=" * 60)
print("TONG KET KET QUA")
print("=" * 60)
best_acc = 0
best_params = None
for params, acc in results:
    marker = ""
    if acc > best_acc:
        best_acc = acc
        best_params = params
    print(f"  {params} => Accuracy: {acc:.4f}")

print(f"\n>>> BO THAM SO TOT NHAT: {best_params}")
print(f">>> ACCURACY CAO NHAT:  {best_acc:.4f}")

# Luu bo tham so tot nhat vao params.yaml
with open("params.yaml", "w") as f:
    f.write("# Sieu tham so cho mo hinh RandomForestClassifier\n")
    f.write("# Thay doi cac gia tri nay giua cac lan chay de thi nghiem (Buoc 1)\n")
    for k, v in best_params.items():
        if v is None:
            f.write(f"{k}: null\n")
        else:
            f.write(f"{k}: {v}\n")

print(f"\n>>> Da cap nhat params.yaml voi bo tham so tot nhat.")
