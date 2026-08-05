# NeuroTriage AI

## AI-assisted Emergency Stroke Triage Platform

### Final Report

**Course:** Management of AI Products  
**Program:** MBA in AI for Business  
**Submitted by:** Saksha Hegde

---

# Table of Contents

1. Product Strategy and Opportunity Framing
2. PM Artifact Pack
3. UX, Workflow, and Trust Design
4. Data, Model, and Evaluation Strategy
5. Business, Economics, and Scaling
6. Ethics, Governance, and Risk Note
7. References
8. Appendix

---

# 1. Product Strategy and Opportunity Framing


## Product Vision

NeuroTriage AI aims to reduce delays in identifying life-threatening intracranial hemorrhage (ICH) cases by intelligently prioritizing emergency CT brain studies within the radiologist's existing workflow. Rather than replacing clinical decision-making, the product assists radiologists in reviewing the most critical patients first, enabling faster diagnosis and improved patient outcomes.

---

## Product Positioning

NeuroTriage AI is an AI-assisted emergency radiology workflow platform designed to prioritize suspected intracranial hemorrhage cases within the existing PACS environment. Unlike standalone diagnostic AI tools, NeuroTriage AI focuses on improving clinical workflow by ensuring that the most urgent patients are reviewed first while keeping radiologists in complete control of diagnosis and treatment decisions.

---

## Jobs-To-Be-Done (JTBD)

> **When I am** reviewing a large number of emergency CT brain studies, 
**I want** the most critical patients to be automatically prioritized 
**so that** I can diagnose life-threatening intracranial hemorrhages earlier without compromising diagnostic accuracy.

### Primary User

Emergency Radiologist

### Supporting Stakeholders

- Emergency Physicians
- Hospital Administration
- Patients

---

## Opportunity Framing

### Why this problem matters

Intracranial hemorrhage is a time-critical medical emergency where early diagnosis directly influences patient survival and long-term neurological outcomes. In busy emergency departments, radiologists often review a large number of CT studies under significant time pressure. Since worklists are generally processed sequentially, critical hemorrhage cases may remain unnoticed until their turn arrives, delaying diagnosis and treatment.

Reducing the time taken to identify and review suspected ICH cases can improve patient outcomes, enhance emergency department efficiency, and reduce the cognitive burden on radiologists.

### Why current alternatives are weak

Current radiology workflows rely primarily on manual worklist management and clinician judgment to identify urgent cases. While experienced radiologists are highly skilled at detecting abnormalities, existing systems provide limited support in prioritizing studies before review.

Some standalone AI applications can detect abnormalities but require radiologists to access separate systems, interrupting their normal workflow. These solutions often function as diagnostic aids rather than workflow optimization tools and therefore provide limited operational benefit.

### Why AI may help

Artificial Intelligence can rapidly analyze CT brain images and estimate the probability of intracranial hemorrhage based on learned imaging patterns. Instead of replacing the radiologist, AI acts as an intelligent triage assistant by prioritizing high-risk studies immediately after image acquisition.

By integrating directly into the existing PACS workflow, AI enables radiologists to review the most urgent patients first while maintaining full clinical control. This Human-in-the-Loop approach combines the speed of AI with the expertise and accountability of clinicians.

---

## Opportunity Matrix

| Opportunity | Business Value | Feasibility | Priority |
|-------------|---------------|------------|----------|
| AI-assisted prioritization of suspected ICH cases | High | High | **P1** |
| AI-generated preliminary radiology report | High | Medium | P2 |
| Multi-condition detection (ICH, ischemic stroke, tumors) | Very High | Low | P3 |
| Emergency radiology analytics dashboard | Medium | High | P4 |

### Selected Opportunity

The first product release will focus exclusively on AI-assisted prioritization of suspected intracranial hemorrhage cases. This delivers immediate clinical value while keeping the MVP focused, feasible, and easy to validate.

---

## Build vs Buy vs Partner/API

### Recommended Path

**Build the workflow platform while integrating an existing AI model for the MVP.**

### Why

The primary value of NeuroTriage AI lies in seamlessly integrating AI into the radiologist's workflow rather than developing a novel image classification model. Leveraging an existing, clinically validated AI model (or a suitable open-source alternative for prototyping) enables faster product development while allowing the team to focus on workflow integration, user experience, and clinical adoption.

As the product matures, proprietary models can be developed or fine-tuned using larger, institution-specific datasets to improve performance and create long-term competitive differentiation.

### Main Trade-offs

| Approach | Advantages | Limitations |
|-----------|------------|-------------|
| Build | Full control, customization, long-term differentiation | Higher development effort and longer time-to-market |
| Buy | Faster implementation, clinically validated solutions may be available | Vendor dependency and limited customization |
| Partner/API | Rapid prototyping and lower upfront investment | Dependency on external providers and limited control over model evolution |

---

## First Wedge

The MVP will address a single, high-impact workflow:

> **Automatically prioritize suspected intracranial hemorrhage (ICH) CT studies within the radiologist's PACS worklist.**

The MVP will:

- Analyze non-contrast CT brain studies immediately after acquisition.
- Estimate the probability of intracranial hemorrhage.
- Assign a confidence score.
- Reorder the radiologist's worklist based on clinical urgency.
- Allow the radiologist to accept, reject, or override AI recommendations.

The MVP will **not** include:

- Automated diagnosis
- Treatment recommendations
- AI-generated radiology reports
- Detection of other neurological conditions
- MRI analysis

By focusing on a single workflow, the product minimizes implementation complexity while maximizing clinical impact and enabling rapid validation during pilot deployment.

---

## Product Principles

The following principles guide all product decisions for NeuroTriage AI and ensure that future enhancements remain aligned with the product vision.

### 1. Assist, Never Replace

AI supports radiologists by prioritizing cases and providing decision support. Final clinical responsibility always remains with the radiologist.

### 2. Prioritize, Don't Diagnose

The primary value of NeuroTriage AI is intelligent worklist prioritization. It is designed to ensure that the right patient is reviewed at the right time rather than to generate autonomous diagnoses.

### 3. Integrate, Don't Disrupt

The product integrates seamlessly into existing PACS workflows, requiring minimal changes to established clinical processes and reducing adoption barriers.

### 4. Trust Through Transparency

Every AI recommendation is accompanied by a confidence score and can be accepted, overridden, or rejected by the radiologist. Transparency is essential for clinician trust and responsible AI adoption.

### 5. Start Focused, Then Scale

The initial MVP addresses one high-impact use case—prioritization of suspected intracranial hemorrhage cases. Additional clinical workflows and AI capabilities will be introduced only after successful validation through pilot deployments.

---

# 2. PM Artifact Pack


## Problem Statement

Emergency radiologists in high-volume hospitals review a continuous stream of CT brain studies with varying levels of clinical urgency. Since worklists are typically processed sequentially, patients with acute intracranial hemorrhage (ICH) may wait behind less critical cases before receiving expert review. These delays can postpone diagnosis and treatment, negatively affecting patient outcomes while increasing cognitive workload on radiologists.

NeuroTriage AI addresses this workflow challenge by intelligently prioritizing suspected intracranial hemorrhage cases within the existing PACS worklist, enabling radiologists to review the most critical patients first while maintaining complete clinical control.

---

## Product Vision

To improve emergency stroke care by ensuring that life-threatening intracranial hemorrhage cases are reviewed at the earliest possible opportunity through AI-assisted workflow prioritization, while preserving radiologist autonomy, clinical accountability, and patient safety.

---

## PRD Summary

### User Problem

Radiologists currently lack an intelligent mechanism to identify the most clinically urgent CT brain studies before beginning image interpretation. As imaging volumes continue to increase, manual prioritization becomes increasingly difficult, resulting in delayed diagnosis of time-critical hemorrhage cases.

### Core Workflow

1. CT brain study is acquired.
2. Images are automatically transferred to PACS.
3. NeuroTriage AI analyzes the CT study in the background.
4. The AI predicts the probability of intracranial hemorrhage.
5. A confidence score is generated.
6. The PACS worklist is reordered based on predicted clinical urgency.
7. The radiologist reviews the prioritized studies.
8. The radiologist confirms, overrides, or rejects the AI recommendation.
9. User feedback is captured for future model improvement.

### AI Role

The AI functions as an intelligent clinical triage assistant. It predicts the likelihood of intracranial hemorrhage and recommends worklist prioritization. The AI never makes autonomous diagnoses or treatment decisions; all clinical decisions remain with the radiologist.

### Risks

- False negatives delaying review of critical hemorrhage cases.
- False positives increasing unnecessary urgent reviews.
- Automation bias causing excessive reliance on AI recommendations.
- Model performance degradation due to data drift.
- Integration challenges with existing PACS infrastructure.

### Fallback Logic

If the AI service becomes unavailable or the prediction confidence falls below a predefined threshold, the system automatically falls back to the standard PACS workflow. CT studies continue to be reviewed according to existing hospital procedures, ensuring uninterrupted patient care.

---

## Feature Prioritization

| Feature | User Value | Effort | Confidence | Priority |
|---------|-----------|--------|------------|----------|
| AI-assisted worklist prioritization | High | Medium | High | **P1** |
| Confidence score visualization | High | Low | High | **P1** |
| Radiologist override capability (Human-in-the-Loop) | High | Low | High | **P1** |
| Explainability visualizations (heatmaps / ROI highlights) | Medium | Medium | Medium | **P2** |
| Feedback-driven model improvement | High | High | Medium | **P2** |
| Workflow analytics dashboard | Medium | Medium | Medium | **P2** |
| Detection of additional hemorrhage subtypes | High | High | Low | **P3** |

---

## MVP Definition

The Minimum Viable Product (MVP) focuses on validating a single high-value workflow:

> **Automatically prioritize suspected intracranial hemorrhage CT studies within the radiologist's PACS worklist.**

The MVP will:

- Analyze non-contrast CT brain studies immediately after acquisition.
- Predict the probability of intracranial hemorrhage.
- Display a confidence score for every prediction.
- Reorder the radiologist's worklist based on predicted urgency.
- Allow radiologists to accept, reject, or override AI recommendations.
- Capture user feedback for future model improvement.

The MVP intentionally excludes:

- Automated diagnosis
- Treatment recommendations
- AI-generated radiology reports
- MRI analysis
- Detection of other neurological conditions

Restricting the MVP to a single workflow minimizes implementation complexity while enabling rapid validation of clinical usefulness, workflow integration, and user acceptance.

---

## Product Evolution Roadmap

### Phase 1 – MVP Validation

Validate the core product hypothesis by demonstrating that AI-assisted worklist prioritization reduces review delays without disrupting existing clinical workflows.

Deliverables:

- AI-assisted prioritization of suspected ICH studies
- Confidence score visualization
- Human-in-the-Loop review
- PACS worklist integration
- Basic system monitoring

---

### Phase 2 – Clinical Expansion

Expand product capabilities to improve clinician trust, usability, and operational effectiveness following successful MVP validation.

Deliverables:

- Explainability visualizations (heatmaps and highlighted regions of interest)
- Feedback-driven model improvement using radiologist validations
- Pilot deployment across multiple departments within the hospital
- Workflow analytics dashboard for operational and adoption metrics

---

### Phase 3 – Enterprise Scale

Transform NeuroTriage AI into an enterprise healthcare platform capable of supporting multiple hospitals while ensuring responsible AI governance.

Deliverables:

- Detection of additional intracranial hemorrhage subtypes (subdural, epidural, intraparenchymal, etc.)
- Multi-hospital deployment
- Continuous model performance monitoring and drift detection
- AI governance framework including audit trails, model versioning, and periodic validation

---

## Success Metrics

### Product Metrics

- Reduction in average Time-to-Review for suspected ICH studies.
- Percentage of high-risk CT studies correctly prioritized.
- Radiologist adoption rate.
- Average radiologist override rate.

### Business Metrics

- Reduction in emergency diagnosis turnaround time.
- Reduction in door-to-treatment time for hemorrhage patients.
- Improvement in emergency department workflow efficiency.
- Improved utilization of existing radiology resources.

### Trust / Guardrail Metrics

- **False Negative Rate:** Percentage of actual hemorrhage cases incorrectly classified as low risk. This is the most critical patient safety metric because missed hemorrhages can delay life-saving treatment.

- **False Positive Rate:** Percentage of normal CT studies incorrectly prioritized as urgent, increasing unnecessary workload for radiologists.

- **AI Confidence Calibration:** Measures whether the AI's confidence score accurately reflects the probability of being correct. Well-calibrated confidence enables clinicians to develop appropriate trust in AI recommendations without becoming over-dependent.

- **Radiologist Override Rate:** Percentage of AI recommendations modified or rejected by radiologists. A consistently high override rate may indicate reduced model performance, poor explainability, or lack of user trust.

- **System Availability During Emergency Operations:** Percentage of time the AI platform remains operational during emergency workflows. If the AI service becomes unavailable, the system must automatically revert to the standard PACS workflow, ensuring uninterrupted patient care.

---

# 3. UX, Workflow, and Trust Design

> *Copy the complete contents of `UX_Workflow_Trust_Design.md` here.*

---

# 4. Data, Model, and Evaluation Strategy

> *Copy the complete contents of `Data_Model_Evaluation_Strategy.md` here.*

---

# 5. Business, Economics, and Scaling

> *Copy the complete contents of `Business_Economics_and_Scaling.md` here.*

---

# 6. Ethics, Governance, and Risk Note

> *Copy the complete contents of `Ethics_Governance_and_Risk_Note.md` here.*

---

# 7. References

1. RSNA Intracranial Hemorrhage Detection Dataset.
2. CQ500: A Large-Scale Annotated Brain CT Dataset for Intracranial Hemorrhage Detection.
3. PlantUML. https://plantuml.com/
4. PyTorch Documentation. https://pytorch.org/
5. FastAPI Documentation. https://fastapi.tiangolo.com/
6. React Documentation. https://react.dev/

---

# 8. Appendix

The detailed supporting artifacts for this project are available in the accompanying GitHub repository under the **Appendix** folder.

These include:

- Product Requirements Document (PRD)
- Product Strategy (Standalone)
- PM Artifact Pack (Standalone)
- PlantUML Source Diagrams
- Workflow Diagrams
- Wireframes
- Roadmap
- Metrics
- Risk Note
- Prototype Screenshots (to be added)
