import pickle
import numpy as np
import pandas as pd
import shap
import lime.lime_tabular
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# 🔹 Load models
with open('diagnosis_model.pkl', 'rb') as file:
    diagnosis_model = pickle.load(file)

with open('disease_model.pkl', 'rb') as file:
    disease_model = pickle.load(file)

# 🔹 Load expected feature list
with open('features_used.pkl', 'rb') as file:
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

# 🔹 Initialize SHAP Explainers (TreeExplainer is efficient for XGBoost)
shap_explainer_diagnosis = shap.TreeExplainer(diagnosis_model)
shap_explainer_disease = shap.TreeExplainer(disease_model)

# 🔹 Fit LIME Explainers using dummy data for structure
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


def predict_with_explanations(form_data_dict):
    try:
        input_df = pd.DataFrame([form_data_dict])
        input_df = input_df.reindex(columns=expected_features, fill_value=0)

        if input_df.sum(axis=1).iloc[0] < 3:
            return {
                "diagnosis": "Warning",
                "message": "Prediction may be less accurate due to limited input."
            }

        # Step 1: Predict Diagnosis
        diagnosis_pred = diagnosis_model.predict(input_df)[0]
        diagnosis_label = "Disease Detected" if diagnosis_pred == 1 else "Healthy"

        result = {
            "diagnosis": diagnosis_label,
            "message": "No Eye Diseases Found." if diagnosis_pred == 0 else "Eye Disease Detected.",
            "explanations": {
                "diagnosis": {},
                "disease": {}
            }
        }

        # Step 2: SHAP for Diagnosis
        shap_diag_vals = shap_explainer_diagnosis.shap_values(input_df)
        shap_diag_expl = sorted(
            zip(expected_features, shap_diag_vals[0]),
            key=lambda x: abs(x[1]),
            reverse=True
        )[:10]
        result["explanations"]["diagnosis"]["shap"] = shap_diag_expl

        # Step 3: LIME for Diagnosis
        lime_diag_exp = lime_explainer_diagnosis.explain_instance(
            input_df.iloc[0].values,
            diagnosis_model.predict_proba,
            num_features=10
        )
        lime_diag_expl = lime_diag_exp.as_list()
        result["explanations"]["diagnosis"]["lime"] = lime_diag_expl

        # If healthy, no need to explain disease
        if diagnosis_pred == 0:
            return result

        # Step 4: Predict Disease
        disease_pred = disease_model.predict(input_df)[0]
        disease_name = disease_mapping.get(disease_pred, "Unknown Disease")
        result["disease"] = disease_name
        result["message"] = f"Eye Disease Detected: {disease_name}"
        result["explanations"]["disease"] = {}
 

        # Step 5: SHAP for Disease
        shap_dis_all = shap_explainer_disease.shap_values(input_df)

        if isinstance(shap_dis_all, list) and disease_pred < len(shap_dis_all):
              shap_dis_vals = shap_dis_all[disease_pred]
        else:
            shap_dis_vals = shap_dis_all[0]  # fallback to something safe to avoid crash

        shap_dis_expl = sorted(
            zip(expected_features, shap_dis_vals[0]),
            key=lambda x: abs(x[1]),
            reverse=True
        )[:10]
        result["explanations"]["disease"]["shap"] = shap_dis_expl

        # Step 6: LIME for Disease
        lime_dis_exp = lime_explainer_disease.explain_instance(
            input_df.iloc[0].values,
            disease_model.predict_proba,
            num_features=10
        )
        lime_dis_expl = lime_dis_exp.as_list()
        result["explanations"]["disease"]["lime"] = lime_dis_expl

        return result

    except Exception as e:
        return {"error": str(e)}





def explain_prediction_visually(result, input_df, title=""):
    """
    Converts SHAP and LIME results into easy-to-read explanations for patients.
    Optionally visualize the SHAP values with a bar chart.
    """
    if "error" in result:
        print("⚠️ Error during prediction:", result["error"])
        return

    print(f"\n📋 Diagnosis Result: {result['diagnosis']}")
    print(f"📝 Message: {result['message']}")

    if result["diagnosis"] == "Healthy":
        print("\n🎉 The model did not detect any signs of eye disease.")
        print("✅ You appear to be healthy based on the provided features.")
        
        # Create a full green healthy chart with smiley + messages
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.set_facecolor('#2ecc71')  # Bright green background

        # Remove axis
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)

        # Add happy emoji and text
        ax.text(0.5, 0.7, '😊', fontsize=60, ha='center', va='center')
        ax.text(0.5, 0.45, 'You are healthy!', fontsize=16, ha='center', va='center', color='white')
        ax.text(0.5, 0.30, "No signs of eye disease detected!", fontsize=12, ha='center', va='center', color='white')

        # Title
        plt.title("No Eye Disease Detected", fontsize=14, color='white')
        plt.tight_layout()
        plt.show()

        return

    # Only elaborate if a disease is detected
    if result["diagnosis"] == "Disease Detected":
        disease = result.get("disease", "Unknown")
        print(f"\n🧬 Disease Identified: {disease}")

        print("\n🔍 SHAP Explanation (Top Contributing Factors):")
        for feature, value in result["explanations"]["disease"]["shap"]:
            impact = "increased" if value > 0 else "reduced"
            print(f"• {feature} {impact} the likelihood of {disease} (impact: {round(abs(value), 4)})")

        print("\n💡 LIME Explanation (Patient-friendly terms):")
        for feature, weight in result["explanations"]["disease"]["lime"]:
            direction = "supports" if weight > 0 else "reduces"
            print(f"• {feature} {direction} the prediction for {disease} (weight: {round(weight, 4)})")

        # OPTIONAL: Visual bar chart for SHAP (run only in interactive environment)
        shap_values = result["explanations"]["disease"]["shap"]
        if shap_values:
            features, values = zip(*shap_values)
            colors = ['green' if v > 0 else 'red' for v in values]

            plt.figure(figsize=(10, 5))
            plt.barh(features, values, color=colors)
            plt.xlabel("SHAP Value (Impact on Prediction)")
            plt.title(f"Top 10 Influential Features for {disease}")
            plt.gca().invert_yaxis()
            red_patch = mpatches.Patch(color='red', label='Negative Impact')
            green_patch = mpatches.Patch(color='green', label='Positive Impact')
            plt.legend(handles=[green_patch, red_patch])
            plt.tight_layout()
            plt.show()




# 🔹 Run standalone tests
if __name__ == "__main__":
    

    # 🔹 Sample Input for Glaucoma
 glaucoma_input = {'Age': 69.0, 'Intraocular Pressure (IOP)': 19.46, 'Cup-to-Disc Ratio (CDR)': 0.42, 'Pachymetry': 541.51, 'Visual Symptoms_tunnel vision': 1.0, 'Visual Symptoms_halos around lights': 0.0, 'Visual Symptoms_redness in the eye': 0.0, 'Visual Symptoms_blurred vision': 0.0, 'History of Diabetes': 0.0, 'Smoking Status': 0.0, 'Visual Acuity Test Results_20/100': 0.0, 'Visual Acuity Test Results_20/20': 0.0, 'Visual Acuity Test Results_20/30': 0.0, 'Visual Acuity Test Results_20/40': 0.0, 'Visual Acuity Test Results_20/50': 0.0, 'Visual Acuity Test Results_20/70': 0.0, 'Lens Opacity_mild': 0.0, 'Lens Opacity_moderate': 0.0, 'Lens Opacity_severe': 0.0, 'Glare Sensitivity_mild': 0.0, 'Glare Sensitivity_none': 0.0, 'Glare Sensitivity_severe': 0.0, 'UV Exposure_high': 0.0, 'UV Exposure_low': 0.0, 'UV Exposure_medium': 0.0, 'Visual Symptoms_frequent changes in vision': 0.0, 'Visual Symptoms_no visible symptoms': 0.0, 'Retinal Thickness': 248.16244677258328, 'Microaneurysms Count': 2.0, 'Hemorrhages Count': 3.0, 'Visual Symptoms_blotches of dark vision': 0.0, 'Visual Symptoms_fluffy white patches in vision': 0.0, 'Visual Symptoms_occasional blurred vision': 0.0, 'Visual Symptoms_small dark spots in vision': 0.0, 'Visual Symptoms_seeing dark spots': 0.0, 'Visual Symptoms_sudden vision loss': 0.0, 'Visual Symptoms_distorted vision': 0.0, 'Visual Symptoms_lines appear wavy': 0.0, 'Visual Symptoms_mild eye strain': 0.0, 'Visual Symptoms_difficulty reading': 0.0, 'Optical Coherence Tomography (OCT) Results_Early CNV': 0.0, 'Optical Coherence Tomography (OCT) Results_Normal': 0.0, 'Optical Coherence Tomography (OCT) Results_Scarred/End-stage CNV': 0.0, 'Fluorescein Angiography Results_Early Neovascularization': 0.0, 'Fluorescein Angiography Results_No Neovascularization': 0.0, 'Visual Symptoms_floaters': 0.0, 'Visual Symptoms_color vision changes': 0.0, 'Visual Acuity Test Results_20/200': 0.0, 'Visual Acuity Test Results_20/60': 0.0, 'Visual Acuity Test Results_20/80': 0.0, 'Lens Status_Cortical cataract': 0.0, 'Lens Status_Normal': 0.0, 'Lens Status_Nuclear cataract': 0.0, 'Lens Status_Posterior subcapsular cataract': 0.0, 'BMI': 28.132697211774943, 'Blood Pressure': 144.0, 'Cholesterol Levels': 200.0, 'Visual Symptoms_blind spots': 0.0, 'Visual Symptoms_light sensitivity': 0.0, 'Visual Symptoms_night vision problems': 0.0} 
 

# 🔹 Sample Input for Cataract
 cataract_input = {'Age': 78.0, 'Intraocular Pressure (IOP)': 19.0, 'Cup-to-Disc Ratio (CDR)': 0.55, 'Pachymetry': 549.335, 'Visual Symptoms_tunnel vision': 0.0, 'Visual Symptoms_halos around lights': 0.0, 'Visual Symptoms_redness in the eye': 0.0, 'Visual Symptoms_blurred vision': 1.0, 'History of Diabetes': 0.0, 'Smoking Status': 0.0, 'Visual Acuity Test Results_20/100': 0.0, 'Visual Acuity Test Results_20/20': 0.0, 'Visual Acuity Test Results_20/30': 0.0, 'Visual Acuity Test Results_20/40': 0.0, 'Visual Acuity Test Results_20/50': 0.0, 'Visual Acuity Test Results_20/70': 1.0, 'Lens Opacity_mild': 0.0, 'Lens Opacity_moderate': 0.0, 'Lens Opacity_severe': 1.0, 'Glare Sensitivity_mild': 0.0, 'Glare Sensitivity_none': 1.0, 'Glare Sensitivity_severe': 0.0, 'UV Exposure_high': 0.0, 'UV Exposure_low': 0.0, 'UV Exposure_medium': 1.0, 'Visual Symptoms_frequent changes in vision': 0.0, 'Visual Symptoms_no visible symptoms': 0.0, 'Retinal Thickness': 248.16244677258328, 'Microaneurysms Count': 2.0, 'Hemorrhages Count': 3.0, 'Visual Symptoms_blotches of dark vision': 0.0, 'Visual Symptoms_fluffy white patches in vision': 0.0, 'Visual Symptoms_occasional blurred vision': 0.0, 'Visual Symptoms_small dark spots in vision': 0.0, 'Visual Symptoms_seeing dark spots': 0.0, 'Visual Symptoms_sudden vision loss': 0.0, 'Visual Symptoms_distorted vision': 0.0, 'Visual Symptoms_lines appear wavy': 0.0, 'Visual Symptoms_mild eye strain': 0.0, 'Visual Symptoms_difficulty reading': 0.0, 'Optical Coherence Tomography (OCT) Results_Early CNV': 0.0, 'Optical Coherence Tomography (OCT) Results_Normal': 0.0, 'Optical Coherence Tomography (OCT) Results_Scarred/End-stage CNV': 0.0, 'Fluorescein Angiography Results_Early Neovascularization': 0.0, 'Fluorescein Angiography Results_No Neovascularization': 0.0, 'Visual Symptoms_floaters': 0.0, 'Visual Symptoms_color vision changes': 0.0, 'Visual Acuity Test Results_20/200': 0.0, 'Visual Acuity Test Results_20/60': 0.0, 'Visual Acuity Test Results_20/80': 0.0, 'Lens Status_Cortical cataract': 0.0, 'Lens Status_Normal': 0.0, 'Lens Status_Nuclear cataract': 0.0, 'Lens Status_Posterior subcapsular cataract': 0.0, 'BMI': 28.132697211774943, 'Blood Pressure': 144.0, 'Cholesterol Levels': 200.0, 'Visual Symptoms_blind spots': 0.0, 'Visual Symptoms_light sensitivity': 0.0, 'Visual Symptoms_night vision problems': 0.0} 
 

# 🔹 Sample Input for Diabetic Retinopathy
 diabetic_retinopathy_input = {'Age': 61.0, 'Intraocular Pressure (IOP)': 19.0, 'Cup-to-Disc Ratio (CDR)': 0.55, 'Pachymetry': 549.335, 'Visual Symptoms_tunnel vision': 0.0, 'Visual Symptoms_halos around lights': 0.0, 'Visual Symptoms_redness in the eye': 0.0, 'Visual Symptoms_blurred vision': 0.0, 'History of Diabetes': 0.0, 'Smoking Status': 1.0, 'Visual Acuity Test Results_20/100': 0.0, 'Visual Acuity Test Results_20/20': 0.0, 'Visual Acuity Test Results_20/30': 0.0, 'Visual Acuity Test Results_20/40': 0.0, 'Visual Acuity Test Results_20/50': 0.0, 'Visual Acuity Test Results_20/70': 0.0, 'Lens Opacity_mild': 0.0, 'Lens Opacity_moderate': 0.0, 'Lens Opacity_severe': 0.0, 'Glare Sensitivity_mild': 0.0, 'Glare Sensitivity_none': 0.0, 'Glare Sensitivity_severe': 0.0, 'UV Exposure_high': 0.0, 'UV Exposure_low': 0.0, 'UV Exposure_medium': 0.0, 'Visual Symptoms_frequent changes in vision': 0.0, 'Visual Symptoms_no visible symptoms': 0.0, 'Retinal Thickness': 203.441736961152, 'Microaneurysms Count': 4.0, 'Hemorrhages Count': 3.0, 'Visual Symptoms_blotches of dark vision': 0.0, 'Visual Symptoms_fluffy white patches in vision': 0.0, 'Visual Symptoms_occasional blurred vision': 1.0, 'Visual Symptoms_small dark spots in vision': 0.0, 'Visual Symptoms_seeing dark spots': 0.0, 'Visual Symptoms_sudden vision loss': 0.0, 'Visual Symptoms_distorted vision': 0.0, 'Visual Symptoms_lines appear wavy': 0.0, 'Visual Symptoms_mild eye strain': 0.0, 'Visual Symptoms_difficulty reading': 0.0, 'Optical Coherence Tomography (OCT) Results_Early CNV': 0.0, 'Optical Coherence Tomography (OCT) Results_Normal': 0.0, 'Optical Coherence Tomography (OCT) Results_Scarred/End-stage CNV': 0.0, 'Fluorescein Angiography Results_Early Neovascularization': 0.0, 'Fluorescein Angiography Results_No Neovascularization': 0.0, 'Visual Symptoms_floaters': 0.0, 'Visual Symptoms_color vision changes': 0.0, 'Visual Acuity Test Results_20/200': 0.0, 'Visual Acuity Test Results_20/60': 0.0, 'Visual Acuity Test Results_20/80': 0.0, 'Lens Status_Cortical cataract': 0.0, 'Lens Status_Normal': 0.0, 'Lens Status_Nuclear cataract': 0.0, 'Lens Status_Posterior subcapsular cataract': 0.0, 'BMI': 28.132697211774943, 'Blood Pressure': 144.0, 'Cholesterol Levels': 200.0, 'Visual Symptoms_blind spots': 0.0, 'Visual Symptoms_light sensitivity': 0.0, 'Visual Symptoms_night vision problems': 0.0} 
 

# 🔹 Sample Input for CNV
 cnv_input = {'Age': 67.0, 'Intraocular Pressure (IOP)': 19.0, 'Cup-to-Disc Ratio (CDR)': 0.55, 'Pachymetry': 549.335, 'Visual Symptoms_tunnel vision': 0.0, 'Visual Symptoms_halos around lights': 0.0, 'Visual Symptoms_redness in the eye': 0.0, 'Visual Symptoms_blurred vision': 1.0, 'History of Diabetes': 0.0, 'Smoking Status': 0.0, 'Visual Acuity Test Results_20/100': 0.0, 'Visual Acuity Test Results_20/20': 0.0, 'Visual Acuity Test Results_20/30': 0.0, 'Visual Acuity Test Results_20/40': 0.0, 'Visual Acuity Test Results_20/50': 0.0, 'Visual Acuity Test Results_20/70': 0.0, 'Lens Opacity_mild': 0.0, 'Lens Opacity_moderate': 0.0, 'Lens Opacity_severe': 0.0, 'Glare Sensitivity_mild': 0.0, 'Glare Sensitivity_none': 0.0, 'Glare Sensitivity_severe': 0.0, 'UV Exposure_high': 0.0, 'UV Exposure_low': 0.0, 'UV Exposure_medium': 0.0, 'Visual Symptoms_frequent changes in vision': 0.0, 'Visual Symptoms_no visible symptoms': 0.0, 'Retinal Thickness': 248.16244677258328, 'Microaneurysms Count': 2.0, 'Hemorrhages Count': 3.0, 'Visual Symptoms_blotches of dark vision': 0.0, 'Visual Symptoms_fluffy white patches in vision': 0.0, 'Visual Symptoms_occasional blurred vision': 1.0, 'Visual Symptoms_small dark spots in vision': 0.0, 'Visual Symptoms_seeing dark spots': 0.0, 'Visual Symptoms_sudden vision loss': 0.0, 'Visual Symptoms_distorted vision': 0.0, 'Visual Symptoms_lines appear wavy': 0.0, 'Visual Symptoms_mild eye strain': 0.0, 'Visual Symptoms_difficulty reading': 0.0, 'Optical Coherence Tomography (OCT) Results_Early CNV': 0.0, 'Optical Coherence Tomography (OCT) Results_Normal': 1.0, 'Optical Coherence Tomography (OCT) Results_Scarred/End-stage CNV': 0.0, 'Fluorescein Angiography Results_Early Neovascularization': 0.0, 'Fluorescein Angiography Results_No Neovascularization': 1.0, 'Visual Symptoms_floaters': 0.0, 'Visual Symptoms_color vision changes': 0.0, 'Visual Acuity Test Results_20/200': 0.0, 'Visual Acuity Test Results_20/60': 0.0, 'Visual Acuity Test Results_20/80': 0.0, 'Lens Status_Cortical cataract': 0.0, 'Lens Status_Normal': 0.0, 'Lens Status_Nuclear cataract': 0.0, 'Lens Status_Posterior subcapsular cataract': 0.0, 'BMI': 28.132697211774943, 'Blood Pressure': 144.0, 'Cholesterol Levels': 200.0, 'Visual Symptoms_blind spots': 0.0, 'Visual Symptoms_light sensitivity': 0.0, 'Visual Symptoms_night vision problems': 0.0} 
 

# 🔹 Sample Input for DME
 dme_input = {'Age': 39.0, 'Intraocular Pressure (IOP)': 11.0, 'Cup-to-Disc Ratio (CDR)': 0.55, 'Pachymetry': 549.335, 'Visual Symptoms_tunnel vision': 0.0, 'Visual Symptoms_halos around lights': 0.0, 'Visual Symptoms_redness in the eye': 0.0, 'Visual Symptoms_blurred vision': 0.0, 'History of Diabetes': 0.0, 'Smoking Status': 0.0, 'Visual Acuity Test Results_20/100': 0.0, 'Visual Acuity Test Results_20/20': 0.0, 'Visual Acuity Test Results_20/30': 0.0, 'Visual Acuity Test Results_20/40': 0.0, 'Visual Acuity Test Results_20/50': 0.0, 'Visual Acuity Test Results_20/70': 0.0, 'Lens Opacity_mild': 0.0, 'Lens Opacity_moderate': 0.0, 'Lens Opacity_severe': 0.0, 'Glare Sensitivity_mild': 0.0, 'Glare Sensitivity_none': 0.0, 'Glare Sensitivity_severe': 0.0, 'UV Exposure_high': 0.0, 'UV Exposure_low': 0.0, 'UV Exposure_medium': 0.0, 'Visual Symptoms_frequent changes in vision': 0.0, 'Visual Symptoms_no visible symptoms': 0.0, 'Retinal Thickness': 248.16244677258328, 'Microaneurysms Count': 2.0, 'Hemorrhages Count': 3.0, 'Visual Symptoms_blotches of dark vision': 0.0, 'Visual Symptoms_fluffy white patches in vision': 0.0, 'Visual Symptoms_occasional blurred vision': 0.0, 'Visual Symptoms_small dark spots in vision': 0.0, 'Visual Symptoms_seeing dark spots': 0.0, 'Visual Symptoms_sudden vision loss': 0.0, 'Visual Symptoms_distorted vision': 0.0, 'Visual Symptoms_lines appear wavy': 0.0, 'Visual Symptoms_mild eye strain': 0.0, 'Visual Symptoms_difficulty reading': 0.0, 'Optical Coherence Tomography (OCT) Results_Early CNV': 0.0, 'Optical Coherence Tomography (OCT) Results_Normal': 0.0, 'Optical Coherence Tomography (OCT) Results_Scarred/End-stage CNV': 0.0, 'Fluorescein Angiography Results_Early Neovascularization': 0.0, 'Fluorescein Angiography Results_No Neovascularization': 0.0, 'Visual Symptoms_floaters': 0.0, 'Visual Symptoms_color vision changes': 0.0, 'Visual Acuity Test Results_20/200': 0.0, 'Visual Acuity Test Results_20/60': 0.0, 'Visual Acuity Test Results_20/80': 0.0, 'Lens Status_Cortical cataract': 0.0, 'Lens Status_Normal': 0.0, 'Lens Status_Nuclear cataract': 0.0, 'Lens Status_Posterior subcapsular cataract': 0.0, 'BMI': 28.132697211774943, 'Blood Pressure': 144.0, 'Cholesterol Levels': 200.0, 'Visual Symptoms_blind spots': 0.0, 'Visual Symptoms_light sensitivity': 0.0, 'Visual Symptoms_night vision problems': 0.0}
 

# 🔹 Sample Input for Drusen
 drusen_input = {'Age': 89.0, 'Intraocular Pressure (IOP)': 19.0, 'Cup-to-Disc Ratio (CDR)': 0.55, 'Pachymetry': 549.335, 'Visual Symptoms_tunnel vision': 0.0, 'Visual Symptoms_halos around lights': 0.0, 'Visual Symptoms_redness in the eye': 0.0, 'Visual Symptoms_blurred vision': 0.0, 'History of Diabetes': 0.0, 'Smoking Status': 1.0, 'Visual Acuity Test Results_20/100': 0.0, 'Visual Acuity Test Results_20/20': 0.0, 'Visual Acuity Test Results_20/30': 0.0, 'Visual Acuity Test Results_20/40': 0.0, 'Visual Acuity Test Results_20/50': 0.0, 'Visual Acuity Test Results_20/70': 0.0, 'Lens Opacity_mild': 0.0, 'Lens Opacity_moderate': 0.0, 'Lens Opacity_severe': 0.0, 'Glare Sensitivity_mild': 0.0, 'Glare Sensitivity_none': 0.0, 'Glare Sensitivity_severe': 0.0, 'UV Exposure_high': 0.0, 'UV Exposure_low': 0.0, 'UV Exposure_medium': 0.0, 'Visual Symptoms_frequent changes in vision': 0.0, 'Visual Symptoms_no visible symptoms': 0.0, 'Retinal Thickness': 248.16244677258328, 'Microaneurysms Count': 2.0, 'Hemorrhages Count': 3.0, 'Visual Symptoms_blotches of dark vision': 0.0, 'Visual Symptoms_fluffy white patches in vision': 0.0, 'Visual Symptoms_occasional blurred vision': 0.0, 'Visual Symptoms_small dark spots in vision': 0.0, 'Visual Symptoms_seeing dark spots': 0.0, 'Visual Symptoms_sudden vision loss': 0.0, 'Visual Symptoms_distorted vision': 1.0, 'Visual Symptoms_lines appear wavy': 0.0, 'Visual Symptoms_mild eye strain': 0.0, 'Visual Symptoms_difficulty reading': 0.0, 'Optical Coherence Tomography (OCT) Results_Early CNV': 0.0, 'Optical Coherence Tomography (OCT) Results_Normal': 0.0, 'Optical Coherence Tomography (OCT) Results_Scarred/End-stage CNV': 0.0, 'Fluorescein Angiography Results_Early Neovascularization': 0.0, 'Fluorescein Angiography Results_No Neovascularization': 0.0, 'Visual Symptoms_floaters': 0.0, 'Visual Symptoms_color vision changes': 0.0, 'Visual Acuity Test Results_20/200': 0.0, 'Visual Acuity Test Results_20/60': 0.0, 'Visual Acuity Test Results_20/80': 0.0, 'Lens Status_Cortical cataract': 0.0, 'Lens Status_Normal': 0.0, 'Lens Status_Nuclear cataract': 0.0, 'Lens Status_Posterior subcapsular cataract': 0.0, 'BMI': 27.7, 'Blood Pressure': 178.0, 'Cholesterol Levels': 229.0, 'Visual Symptoms_blind spots': 0.0, 'Visual Symptoms_light sensitivity': 0.0, 'Visual Symptoms_night vision problems': 0.0} 

#sample input for HealthyPatient
 healthy_input = {
    'Age': 35.0,
    'Intraocular Pressure (IOP)': 15.0,
    'Cup-to-Disc Ratio (CDR)': 0.3,
    'Pachymetry': 550.0,
    'Visual Symptoms_tunnel vision': 0.0,
    'Visual Symptoms_halos around lights': 0.0,
    'Visual Symptoms_redness in the eye': 0.0,
    'Visual Symptoms_blurred vision': 0.0,
    'History of Diabetes': 0.0,
    'Smoking Status': 0.0,
    'Visual Acuity Test Results_20/20': 1.0,
    'Visual Acuity Test Results_20/30': 0.0,
    'Visual Acuity Test Results_20/40': 0.0,
    'Visual Acuity Test Results_20/50': 0.0,
    'Visual Acuity Test Results_20/70': 0.0,
    'Visual Acuity Test Results_20/100': 0.0,
    'Lens Opacity_mild': 0.0,
    'Lens Opacity_moderate': 0.0,
    'Lens Opacity_severe': 0.0,
    'Glare Sensitivity_mild': 0.0,
    'Glare Sensitivity_none': 1.0,
    'Glare Sensitivity_severe': 0.0,
    'UV Exposure_high': 0.0,
    'UV Exposure_medium': 0.0,
    'UV Exposure_low': 1.0,
    'Visual Symptoms_frequent changes in vision': 0.0,
    'Visual Symptoms_no visible symptoms': 1.0,
    'Retinal Thickness': 250.0,
    'Microaneurysms Count': 0.0,
    'Hemorrhages Count': 0.0,
    'Visual Symptoms_blotches of dark vision': 0.0,
    'Visual Symptoms_fluffy white patches in vision': 0.0,
    'Visual Symptoms_occasional blurred vision': 0.0,
    'Visual Symptoms_small dark spots in vision': 0.0,
    'Visual Symptoms_seeing dark spots': 0.0,
    'Visual Symptoms_sudden vision loss': 0.0,
    'Visual Symptoms_distorted vision': 0.0,
    'Visual Symptoms_lines appear wavy': 0.0,
    'Visual Symptoms_mild eye strain': 0.0,
    'Visual Symptoms_difficulty reading': 0.0,
    'Optical Coherence Tomography (OCT) Results_Early CNV': 0.0,
    'Optical Coherence Tomography (OCT) Results_Normal': 1.0,
    'Optical Coherence Tomography (OCT) Results_Scarred/End-stage CNV': 0.0,
    'Fluorescein Angiography Results_Early Neovascularization': 0.0,
    'Fluorescein Angiography Results_No Neovascularization': 1.0,
    'Visual Symptoms_floaters': 0.0,
    'Visual Symptoms_color vision changes': 0.0,
    'Visual Acuity Test Results_20/200': 0.0,
    'Visual Acuity Test Results_20/60': 0.0,
    'Visual Acuity Test Results_20/80': 0.0,
    'Lens Status_Cortical cataract': 0.0,
    'Lens Status_Normal': 1.0,
    'Lens Status_Nuclear cataract': 0.0,
    'Lens Status_Posterior subcapsular cataract': 0.0,
    'BMI': 22.5,
    'Blood Pressure': 120.0,
    'Cholesterol Levels': 170.0,
    'Visual Symptoms_blind spots': 0.0,
    'Visual Symptoms_light sensitivity': 0.0,
    'Visual Symptoms_night vision problems': 0.0
}




print("\n🧪 Glaucoma Test:")
result = predict_with_explanations(glaucoma_input)
explain_prediction_visually(result, glaucoma_input, title="Glaucoma Test")

print("\n🧪 Cataract Test:")
result = predict_with_explanations(cataract_input)
explain_prediction_visually(result, cataract_input, title="Cataract Test")


print("\n🧪 Diabetic Retinopathy Test:")
result = predict_with_explanations(diabetic_retinopathy_input)
explain_prediction_visually(result, diabetic_retinopathy_input, title="Diabetic Retinopathy Test")


print("\n🧪 CNV Test:")
result = predict_with_explanations(cnv_input)
explain_prediction_visually(result, cnv_input, title="CNV Test")


print("\n🧪 DME Test:")
result = predict_with_explanations(dme_input)
explain_prediction_visually(result, dme_input, title="DME Test")


print("\n🧪 Drusen Test:")
result = predict_with_explanations(drusen_input)
explain_prediction_visually(result, drusen_input, title="Drusen Test")

print("\n🧪 Healthy Test:")
result = predict_with_explanations(healthy_input)
explain_prediction_visually(result, healthy_input)



