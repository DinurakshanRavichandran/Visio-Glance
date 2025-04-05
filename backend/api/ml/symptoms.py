import os
import pickle
import numpy as np
import pandas as pd
import shap
import lime.lime_tabular
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_cors import CORS
import traceback

# 🔹 Blueprint setup
symptoms_bp = Blueprint("symptoms_bp", __name__)
CORS(symptoms_bp)

# 🔹 Set current absolute path
current_dir = os.path.dirname(os.path.abspath(__file__))

# 🔹 Load models
with open(os.path.join(current_dir, 'diagnosis_model.pkl'), 'rb') as file:
    diagnosis_model = pickle.load(file)

with open(os.path.join(current_dir, 'disease_model.pkl'), 'rb') as file:
    disease_model = pickle.load(file)

# 🔹 Load expected feature list
with open(os.path.join(current_dir, 'features_used.pkl'), 'rb') as file:
    expected_features = pickle.load(file)

# 🔹 Disease label mapping
disease_mapping = {
    0: "Glaucoma",
    1: "Cataract",
    2: "Diabetic Retinopathy",
    3: "CNV",
    4: "DME",
    5: "Drusen"
}

# 🔹 Initialize SHAP & LIME explainers
shap_explainer_diagnosis = shap.TreeExplainer(diagnosis_model)
shap_explainer_disease = shap.TreeExplainer(disease_model)

dummy_data = np.zeros((1, len(expected_features)))

lime_explainer_diagnosis = lime.lime_tabular.LimeTabularExplainer(
    training_data=dummy_data,
    feature_names=expected_features,
    class_names=["Healthy", "Disease"],
    mode="classification"
)

lime_explainer_disease = lime.lime_tabular.LimeTabularExplainer(
    training_data=dummy_data,
    feature_names=expected_features,
    class_names=list(disease_mapping.values()),
    mode="classification"
)

# ────────────────────────────────────────────────
# 🔍 Core Prediction Logic
# ────────────────────────────────────────────────
def predict_with_explanations(form_data_dict):
    try:
        input_df = pd.DataFrame([form_data_dict])
        input_df = input_df.reindex(columns=expected_features, fill_value=0)

        if input_df.sum(axis=1).iloc[0] < 3:
            return {
                "diagnosis": "Warning",
                "message": "Prediction may be less accurate due to limited input."
            }, input_df

        diagnosis_pred = diagnosis_model.predict(input_df)[0]
        diagnosis_label = "Disease Detected" if diagnosis_pred == 1 else "Healthy"

        result = {
            "diagnosis": diagnosis_label,
            "message": "No Eye Diseases Found." if diagnosis_pred == 0 else "Eye Disease Detected.",
            "explanations": {"diagnosis": {}, "disease": {}}
        }

        # SHAP for diagnosis
        shap_diag_vals = shap_explainer_diagnosis.shap_values(input_df)
        shap_diag_vals = shap_diag_vals[0] if isinstance(shap_diag_vals, list) else shap_diag_vals
        shap_diag_vals = shap_diag_vals.flatten()

        shap_diag_expl = sorted(zip(expected_features, shap_diag_vals), key=lambda x: abs(x[1]), reverse=True)[:10]
        result["explanations"]["diagnosis"]["shap"] = [(str(f), float(v)) for f, v in shap_diag_expl]

        # LIME for diagnosis
        lime_diag_exp = lime_explainer_diagnosis.explain_instance(
            input_df.iloc[0].values,
            diagnosis_model.predict_proba,
            num_features=10
        )
        result["explanations"]["diagnosis"]["lime"] = [(str(f), float(v)) for f, v in lime_diag_exp.as_list()]

        if diagnosis_pred == 0:
            return result, input_df

        # Disease classification
        disease_pred = disease_model.predict(input_df)[0]
        disease_name = disease_mapping.get(disease_pred, "Unknown Disease")
        result["disease"] = disease_name
        result["message"] = f"Eye Disease Detected: {disease_name}"

        # SHAP for disease
        shap_dis_all = shap_explainer_disease.shap_values(input_df)
        shap_dis_vals = shap_dis_all[disease_pred] if isinstance(shap_dis_all, list) else shap_dis_all
        shap_dis_vals = shap_dis_vals.flatten()

        shap_dis_expl = sorted(zip(expected_features, shap_dis_vals), key=lambda x: abs(x[1]), reverse=True)[:10]
        result["explanations"]["disease"]["shap"] = [(str(f), float(v)) for f, v in shap_dis_expl]

        # LIME for disease
        lime_dis_exp = lime_explainer_disease.explain_instance(
            input_df.iloc[0].values,
            disease_model.predict_proba,
            num_features=10
        )
        result["explanations"]["disease"]["lime"] = [(str(f), float(v)) for f, v in lime_dis_exp.as_list()]

        return result, input_df

    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}, pd.DataFrame()

# ────────────────────────────────────────────────
# 🖼️ SHAP + LIME Visualization
# ────────────────────────────────────────────────
def explain_prediction_visually(result, input_df, title="", save_dir=None):
    try:
        if save_dir is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            save_dir = os.path.abspath(os.path.join(script_dir, '..', '..', 'static', 'xai'))

        os.makedirs(save_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if "error" in result:
            return None

        if result["diagnosis"] == "Healthy":
            fig, ax = plt.subplots(figsize=(4, 4))
            ax.set_facecolor('#2ecc71')
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)

            ax.text(0.5, 0.7, '😊', fontsize=60, ha='center', va='center')
            ax.text(0.5, 0.45, 'You are Healthy!', fontsize=16, ha='center', va='center', color='white')
            ax.text(0.5, 0.30, "No Signs of Eye Diseases Detected!", fontsize=12, ha='center', va='center', color='white')
            plt.title("No Eye Disease Detected", fontsize=14, color='white')
            plt.tight_layout()

            save_path = os.path.join(save_dir, f"healthy_summary_{timestamp}.png")
            plt.savefig(save_path, bbox_inches='tight')
            plt.close()
            return os.path.basename(save_path)

        disease = result.get("disease", "Unknown")
        shap_values = result["explanations"]["disease"]["shap"]
        lime_values = result["explanations"]["disease"]["lime"]

        if shap_values and lime_values:
            shap_features, shap_importances = zip(*shap_values)
            lime_features, lime_weights = zip(*lime_values)

            shap_colors = ['#ff7f0e' if val > 0 else '#1f77b4' for val in shap_importances]
            lime_colors = ['#ff7f0e' if val > 0 else '#1f77b4' for val in lime_weights]

            fig, axes = plt.subplots(nrows=2, figsize=(10, 9))
            plt.suptitle(f"Disease Identified – {disease}", fontsize=16, fontweight='bold')

            axes[0].barh(shap_features, shap_importances, color=shap_colors)
            axes[0].set_title(f"SHAP - Top Features Influencing {disease}", fontsize=12)
            axes[0].invert_yaxis()
            axes[0].set_xlabel("SHAP Value (Impact)")

            axes[1].barh(lime_features, lime_weights, color=lime_colors)
            axes[1].set_title(f"LIME - Local Explanation for {disease}", fontsize=12)
            axes[1].invert_yaxis()
            axes[1].set_xlabel("LIME Weight (Impact)")

            plt.tight_layout(rect=[0, 0, 1, 0.95])
            legend_patches = [
                mpatches.Patch(color='#ff7f0e', label='Positive Contribution'),
                mpatches.Patch(color='#1f77b4', label='Negative Contribution')
            ]
            plt.legend(handles=legend_patches, loc='lower right')

            save_path = os.path.join(save_dir, f"{disease}_shap_lime_combined_{timestamp}.png")
            plt.savefig(save_path, bbox_inches='tight')
            plt.close()
            return os.path.basename(save_path)

        return None
    except Exception as e:
        traceback.print_exc()
        return None

# ────────────────────────────────────────────────
# 🚀 API Route
# ────────────────────────────────────────────────
@symptoms_bp.route("/predict", methods=["POST"])
def predict_route():
    try:
        data = request.json
        print("📥 Received data:", data)

        result, input_df = predict_with_explanations(data)

        if isinstance(result, dict) and "error" in result:
            return jsonify(result), 400

        filename = explain_prediction_visually(result, input_df)
        result["xai_image"] = filename
        return jsonify(result)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
