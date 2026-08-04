# Ethics, Governance, and Risk Note

## Main Risks

| Priority | Risk | Mitigation |
|----------|------|------------|
| **High** | False Negative Prediction (Missed ICH) | Human-in-the-Loop review, continuous model evaluation, and conservative prioritization policy. |
| **High** | Over-reliance on AI Recommendations | AI supports, but never replaces, clinical judgement. Confidence scores and explainability are always displayed. |
| **Medium** | Workflow Disruption | Pilot deployment, continuous performance monitoring, and seamless PACS integration. |

---

## Harm Scenarios

| Stakeholder | Potential Harm |
|-------------|----------------|
| **Patient** | Delayed diagnosis if intracranial hemorrhage is missed. |
| **Radiologist** | Incorrect prioritization may delay urgent reviews or increase unnecessary workload. |
| **Hospital** | Reduced clinician trust, workflow disruption, and regulatory exposure. |
| **Product Provider** | Reputational damage and loss of customer confidence. |

---

## Controls

| Area | Control |
|------|---------|
| **Guardrails** | AI is used only for worklist prioritization. Final diagnosis always remains the responsibility of the radiologist. |
| **Review Process** | Clinical validation, pilot deployment, and continuous performance monitoring before large-scale rollout. |
| **Escalation Path** | Low-confidence cases receive earlier human review. AI prioritization is suspended if patient safety is compromised. |
| **Logging & Auditability** | AI predictions, radiologist overrides, feedback, and model versions are logged to support traceability, continuous improvement, and regulatory audits. |

---

## Launch Blockers

Product launch should be delayed or suspended if:

- The predefined launch thresholds for **sensitivity, false negative rate, inference time, clinician adoption, and system availability** (defined in the **Evaluation Strategy**) are not achieved.
- Clinical validation identifies unacceptable patient safety risks.
- PACS integration disrupts existing clinical workflows.
- Regulatory or organizational approvals are incomplete.
- Pilot deployment demonstrates low clinician trust or adoption.

These launch blockers ensure that **patient safety, clinician trust, and workflow stability** are validated before NeuroTriage AI progresses to routine clinical deployment.
