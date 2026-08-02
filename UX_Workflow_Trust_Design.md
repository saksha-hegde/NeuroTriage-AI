# UX and Workflow Design

## Main Workflow

NeuroTriage AI is designed to integrate seamlessly into the existing radiology workflow without requiring users to learn a new application. The AI operates silently in the background immediately after a CT brain study is acquired and assists radiologists by intelligently prioritizing suspected intracranial hemorrhage (ICH) cases within the existing PACS worklist.

The user journey is as follows:

1. The patient undergoes a non-contrast CT brain scan.
2. CT images are automatically transferred to the hospital PACS.
3. NeuroTriage AI analyzes the study in the background without requiring any user interaction.
4. The AI predicts the likelihood of intracranial hemorrhage and estimates its confidence.
5. The PACS worklist is reprioritized using the AI assessment and model confidence to ensure that clinically urgent and uncertain cases receive earlier review.
6. The radiologist reviews studies in priority order.
7. When a study is opened, NeuroTriage AI displays its assessment, confidence level, and supporting visual explanation.
8. The radiologist confirms, overrides, or rejects the AI recommendation.
9. Radiologist feedback is captured to support future model improvement.

This workflow improves emergency case prioritization while preserving the existing clinical workflow and ensuring that the radiologist remains responsible for all diagnostic decisions.

---

### Current Workflow

The following diagram illustrates the existing emergency radiology workflow, where CT studies are typically reviewed sequentially without AI-assisted prioritization.

![Current Workflow](images/current-workflow.svg)

*Figure 1. Current emergency radiology workflow.*

---

### Proposed AI-Assisted Workflow

The following diagram illustrates how NeuroTriage AI integrates into the existing workflow by automatically prioritizing suspected intracranial hemorrhage cases while preserving clinician oversight.

![Proposed Workflow](images/proposed_workflow.svg)

*Figure 2. AI-assisted emergency radiology workflow.*

---

## Wireframes / Screens

The MVP consists of two primary interfaces that integrate directly into the existing PACS environment.

### Screen 1 – Prioritized PACS Worklist

Instead of requiring radiologists to interpret raw AI outputs, NeuroTriage AI translates model predictions into clinically meaningful worklist priorities.

### Prioritization Policy

| AI Assessment | Confidence | Priority | Rationale |
|---------------|------------|----------|-----------|
| Suspected ICH | High | 🔴 **Critical** | Strong evidence of a life-threatening condition requiring immediate review. |
| Suspected ICH | Medium | 🟠 **High** | Possible hemorrhage; early review is recommended due to potential clinical risk. |
| No Suspicious Findings | Medium | 🟡 **Moderate** | AI is uncertain. Earlier review helps reduce the chance of a missed hemorrhage. |
| No Suspicious Findings | High | 🟢 **Routine** | AI is confident that no urgent abnormality is present, allowing routine review. |

The prioritization policy combines the AI assessment with the model's confidence rather than relying on prediction alone. The objective is to minimize clinical risk rather than simply rank positive predictions first. Model uncertainty is treated as an indicator for earlier human verification, ensuring that potentially missed hemorrhage cases receive appropriate attention while minimizing unnecessary interruptions for confidently normal studies.

---

### Screen 2 – AI Decision Support Panel

When a radiologist opens a study, NeuroTriage AI presents only the information necessary to support clinical decision-making while avoiding unnecessary AI complexity.

The panel displays:

- AI assessment
- Confidence level
- Highlighted region of interest (heatmap)
- Relevant CT slices
- Radiologist actions:
  - Confirm
  - Override
  - Reject

The final diagnosis always remains the responsibility of the radiologist.

---

## Trust and Explainability

NeuroTriage AI is designed to build clinician trust through transparency while avoiding unnecessary interface complexity. Trust is established by clearly communicating what the AI predicts, how confident it is in that prediction, and allowing the radiologist to make the final clinical decision.

### What does the user need to know?

The radiologist should understand:

- The AI assessment.
- The confidence associated with the prediction.
- Why the AI highlighted the study.
- Which CT image regions contributed to the recommendation.

---

### What must be visible?

The interface displays:

- AI assessment
- Confidence level
- Priority indicator
- Highlighted region of interest
- Relevant CT slices
- Human override options

---

### What should be hidden?

To reduce cognitive overload, the interface intentionally hides:

- Neural network architecture
- Internal model computations and intermediate probabilities
- Training data statistics
- Intermediate feature representations
- Technical implementation details

The objective is to present clinically meaningful information rather than exposing unnecessary AI complexity.

---

## Uncertainty Handling

Since AI predictions are probabilistic, NeuroTriage AI explicitly communicates uncertainty and incorporates it into workflow prioritization.

### High Confidence

High-confidence predictions indicate that the AI has strong confidence in its assessment, allowing the workflow to prioritize cases with greater certainty while still requiring radiologist confirmation.

- High-confidence suspected ICH studies receive the highest priority.
- High-confidence normal studies remain in the routine worklist.

---

### Medium Confidence

Medium-confidence predictions indicate uncertainty. Confidence is treated as a measure of uncertainty rather than correctness.

Instead of hiding this uncertainty, NeuroTriage AI increases review priority to encourage earlier clinical verification. This reduces the likelihood of missing clinically important hemorrhage cases while maintaining radiologist oversight.

---

### Failure or Fallback Behavior

Patient care must never depend solely on AI.

If the AI service becomes unavailable or fails to generate a reliable prediction:

- The standard PACS workflow continues without interruption.
- No AI prioritization is performed.
- No AI recommendation is displayed.
- Radiologists continue following existing hospital procedures.

This fail-safe design ensures uninterrupted emergency care even during AI system failures. AI failure must never result in interruption of clinical services.

---

## Human-in-the-Loop

The following workflow illustrates how NeuroTriage AI incorporates mandatory human review before any clinical decision is made.

![Human-in-the-Loop Workflow](images/human_in_loop_workflow.svg)

*Figure 3. Human-in-the-Loop decision workflow.*

NeuroTriage AI follows a Human-in-the-Loop design philosophy where AI assists but never replaces clinical decision-making.

Human review occurs after AI prioritization but before any diagnosis is made.

The radiologist may:

- Accept the AI recommendation.
- Override the AI prioritization.
- Reject the AI assessment completely.

Every override or rejection is captured as feedback for future model improvement.

NeuroTriage AI assists in prioritization, but every diagnosis remains the responsibility of the radiologist. This Human-in-the-Loop approach balances AI efficiency with clinical expertise, ensuring patient safety while enabling continuous learning from clinician feedback.
