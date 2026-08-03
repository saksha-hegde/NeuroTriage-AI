# Data, Model, and Evaluation Strategy

## Problem as AI Task

The primary objective of NeuroTriage AI is not simply to detect intracranial hemorrhage (ICH), but to help radiologists identify emergency cases earlier within their existing workflow. The business problem is therefore to reduce delays in reviewing critical CT brain studies while maintaining diagnostic safety.

As the AI Product Manager, the first decision is to translate this business objective into an AI problem that can realistically be solved using available data.

The product requires two complementary AI tasks:

| Business Objective | AI Task | Why this AI Task? |
|--------------------|---------|-------------------|
| Detect suspected intracranial hemorrhage | Image Classification | CT scans are medical images where the objective is to classify whether signs of hemorrhage are present. |
| Prioritize studies within the worklist | Confidence-driven Prioritization | Confidence enables the product to distinguish between routine cases and studies that require earlier human review due to either suspected hemorrhage or prediction uncertainty. |

Separating image classification from workflow prioritization is an intentional product decision. The AI model predicts clinical findings, while the product decides how those predictions influence the radiologist's workflow. This ensures that clinical workflow remains under product governance rather than being dictated directly by the model.

---

## Data Sources

The effectiveness of NeuroTriage AI depends on the quality of data available throughout the product lifecycle. Data is therefore treated as a strategic product asset rather than simply a technical requirement.

Three complementary data sources have been identified.

| Data Source | Examples | Product Rationale |
|-------------|----------|-------------------|
| Historical Clinical Data | CT brain scans, radiologist reports, PACS metadata | Provides clinically relevant examples representing the hospital's workflow. |
| Anonymized Medical Imaging Datasets | Curated CT brain dataset containing hemorrhage-positive and normal studies used for prototype development | Provides representative training and evaluation data while protecting patient privacy. |
| Product Feedback Data | Radiologist confirmations, overrides, rejected recommendations | Enables continuous product improvement after deployment by learning from real clinical usage. |

Since NeuroTriage AI operates in a clinical environment, all datasets used for model development will be anonymized to remove patient-identifiable information. Only the minimum data required for model training and evaluation will be retained, following data minimization principles and supporting compliance with applicable healthcare privacy regulations.

---

## Labeling and Ground Truth

The quality of an AI product is directly influenced by the quality of its ground truth.

For NeuroTriage AI, the ground truth will be established using the final diagnosis documented by expert radiologists. Where differences of opinion exist, consensus review will be used to establish the final clinical label.

The model will classify studies into:

- Suspected Intracranial Hemorrhage
- No Suspicious Findings

An important product principle is that AI predictions never become ground truth. Instead, clinician-validated diagnoses remain the authoritative source for both model evaluation and future retraining. This ensures that the AI continuously learns from clinical expertise rather than reinforcing its own mistakes.

---

## Baseline

Before introducing AI, hospitals already possess an effective clinical workflow in which CT brain studies are reviewed sequentially through PACS.

This existing workflow serves as the baseline against which NeuroTriage AI will be evaluated.

Current workflow characteristics include:

- Sequential review of CT studies.
- No automated prioritization of emergency cases.
- Diagnosis depends entirely on manual worklist navigation.
- Critical cases may wait behind routine examinations during busy periods.

The objective of NeuroTriage AI is not to replace this workflow but to enhance it by ensuring that suspected emergency cases reach radiologists earlier without disrupting existing clinical practices.

---

## Model and API Choice

Since the product must analyse CT brain images, an image classification model is the most appropriate AI approach.

A CNN-based image classification model has been selected because Convolutional Neural Networks have consistently demonstrated strong performance in recognising clinically significant patterns within medical images while supporting rapid inference required for emergency care.

The trained model will be exposed through REST APIs, allowing seamless integration with existing PACS infrastructure. This avoids introducing new software for radiologists and supports one of the key product goals: **integrate into the workflow rather than replace it.**

The API provides:

- AI assessment (Suspected ICH / No Suspicious Findings)
- Confidence level
- Priority level
- Explainability information, including highlighted regions of interest

This modular design also allows future model upgrades without affecting the user experience or hospital workflow.

---

## Evaluation Framework

A successful AI product is not measured solely by model accuracy. It must also improve clinical workflow, gain user trust, and deliver measurable business value.

Accordingly, NeuroTriage AI will be evaluated using a balanced set of technical, operational, business, and trust-related metrics.

| Category | Metric | Why it Matters |
|----------|---------|----------------|
| Technical | Sensitivity | Maximise detection of hemorrhage cases. |
| Technical | Specificity | Reduce unnecessary prioritisation of normal studies. |
| Technical | False Negative Rate | Minimise the risk of missing critical patients. |
| Operational | Average Inference Time | Maintain responsiveness within emergency workflows. |
| Business | Time-to-Review Reduction | Demonstrate faster identification of emergency patients. |
| Business | Radiologist Adoption Rate | Measure acceptance of the product in routine practice. |
| Trust | Radiologist Override Rate | Evaluate confidence in AI recommendations. |
| Trust | Confidence Calibration | Ensure confidence scores accurately reflect prediction reliability. |
| Operational | AI System Availability | Ensure uninterrupted clinical support. |

This evaluation framework aligns technical performance with clinical impact, recognising that an accurate model alone does not guarantee a successful AI product.

---

## Launch Thresholds

Before deployment, clear success criteria must be established. Defining these thresholds in advance enables objective go/no-go decisions and prevents subjective evaluation after development.

NeuroTriage AI will progress from pilot deployment to wider clinical adoption only after consistently meeting the following criteria.

| Metric | Target | Product Rationale |
|---------|--------|-------------------|
| Sensitivity | ≥95% | Missing hemorrhage cases has unacceptable clinical consequences. |
| False Negative Rate | ≤2% | Patient safety remains the highest priority. |
| Average Inference Time | ≤10 seconds | Supports emergency department workflow without delays. |
| Radiologist Adoption Rate | ≥85% | Demonstrates that clinicians trust and routinely use the product. |
| AI System Availability | ≥99.5% | Ensures uninterrupted support during emergency operations. |

These thresholds represent not only technical expectations but also the minimum level of product performance required to deliver meaningful clinical value.
