# PM Artifact Pack

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
