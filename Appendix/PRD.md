# Product Requirements Document (PRD)

# NeuroTriage AI

## AI-assisted Emergency Stroke Triage Platform

**Version:** 1.0  
**Status:** Draft  
**Product Owner:** Saksha Hegde  
**Course:** Management of AI Products  
**Program:** MBA in AI for Business

---

# Revision History

| Version | Date | Author | Description |
|----------|------|--------|-------------|
| 1.0 | 05-Aug-2026 | Saksha Hegde | Initial Product Requirements Document |

---

# Table of Contents

1. Document Overview
2. Product Principles
3. Product Overview
4. Product Goals
5. Success Metrics
6. Stakeholders
7. User Personas
8. Functional Requirements
9. Non-Functional Requirements
10. User Stories
11. MVP Scope
12. Future Enhancements
13. Requirements Traceability Matrix

---

# 1. Document Overview

## Purpose

This document defines the functional and non-functional requirements for **NeuroTriage AI**, an AI-assisted emergency stroke triage platform.

It serves as the primary specification for engineering, UX, AI, and clinical teams responsible for building and validating the MVP.

The objective of this document is to ensure that all stakeholders have a common understanding of:

- the problem being solved,
- expected product behaviour,
- user workflow,
- business rules,
- product scope,
- and acceptance criteria.

---

## Product Scope

The MVP focuses on assisting radiologists in prioritizing suspected intracranial hemorrhage (ICH) cases immediately after CT brain acquisition.

The product provides:

- AI-assisted worklist prioritization
- AI confidence scoring
- AI-assisted reading support
- Radiologist feedback capture

The product does **not** replace clinical diagnosis.

---

## Intended Audience

This document is intended for:

- Product Management
- Software Engineering
- AI Engineering
- UX Design
- Clinical Validation Team
- Project Stakeholders

---

# 2. Product Principles

Every design and engineering decision shall align with the following product principles.

| Principle | Description |
|-----------|-------------|
| **AI Assists, Never Replaces** | AI supports prioritization while the radiologist remains responsible for diagnosis. |
| **Workflow Before Technology** | The product integrates into existing PACS workflows instead of introducing new workflows. |
| **Patient Safety First** | When uncertainty exists, the product favours earlier human review rather than increased automation. |
| **Transparency Builds Trust** | Every AI recommendation includes confidence and explainability information. |
| **Deliver Clinical Value** | Product success is measured by improved workflow efficiency and patient outcomes rather than AI accuracy alone. |

---

# 3. Product Overview

NeuroTriage AI is an AI-assisted clinical decision support product that intelligently prioritizes emergency CT brain studies within the radiologist's existing PACS worklist.

Rather than replacing the radiologist, the product continuously analyses newly acquired CT studies and assists clinicians by highlighting suspected intracranial hemorrhage cases that require earlier review.

The product is organised into three logical subsystems.

---

## Subsystem 1 – AI Triage Engine

Responsible for:

- Receiving newly acquired CT studies
- Performing AI inference
- Predicting suspected intracranial hemorrhage
- Calculating AI confidence
- Assigning study priority

This subsystem operates entirely in the background without requiring user interaction.

---

## Subsystem 2 – PACS Worklist Experience

Responsible for:

- Displaying incoming CT studies
- Showing AI processing status
- Automatically reprioritizing completed studies
- Presenting clear visual priority indicators

This subsystem delivers the primary workflow benefit of the product.

---

## Subsystem 3 – Reading Experience

Responsible for:

- Displaying CT images
- Presenting AI findings
- Displaying confidence information
- Showing explainability overlays
- Capturing radiologist feedback

This subsystem supports informed clinical decision-making while maintaining clinician control.

---

# 4. Product Goals

| Goal Category | Objective |
|--------------|-----------|
| **Clinical** | Reduce the time required to identify suspected intracranial hemorrhage cases. |
| **Workflow** | Integrate AI seamlessly into the existing PACS workflow with minimal additional user interaction. |
| **Trust** | Increase clinician confidence through transparent AI recommendations and explainability. |
| **Business** | Deliver measurable workflow improvements while providing a scalable enterprise solution. |

---

# 5. Success Metrics

The success of NeuroTriage AI will be measured using both product and technical outcomes.

| Category | Success Metric |
|-----------|----------------|
| Clinical | Reduced Time-to-Review for suspected ICH cases |
| Technical | High Sensitivity with low False Negative Rate |
| Operational | Low AI inference time |
| User | High Radiologist Adoption Rate |
| Trust | Low Radiologist Override Rate |
| Business | Successful pilot deployment and enterprise adoption |

Detailed launch thresholds are defined in the **Data, Model, and Evaluation Strategy** document.

---

# 6. Stakeholders

| Stakeholder | Responsibility |
|--------------|---------------|
| Radiologist | Reviews prioritized studies and makes the final diagnosis. |
| Emergency Physician | Uses earlier radiology findings to support patient management. |
| Hospital Administrator | Evaluates workflow efficiency and operational value. |
| Product Manager | Owns product vision, roadmap, and feature prioritization. |
| AI Engineering Team | Develops and maintains AI models. |
| Software Engineering Team | Develops and maintains the application. |
| Clinical Validation Team | Validates product performance before deployment. |

---

# 7. User Personas

## Primary Persona – Radiologist

**Primary Goal**

Review emergency CT studies as early as possible without increasing workload.

**Pain Points**

- High imaging volumes.
- Difficulty identifying urgent cases.
- Time pressure during reporting.
- Limited trust in opaque AI systems.

---

## Secondary Persona – Emergency Physician

**Primary Goal**

Receive imaging results earlier to support timely treatment decisions.

---

## Tertiary Persona – Hospital Administrator

**Primary Goal**

Improve emergency workflow efficiency while ensuring safe and sustainable adoption of AI technologies.

---

# 8. Functional Requirements and Product Behaviour

The NeuroTriage AI MVP consists of four primary product behaviours that together support the emergency radiology workflow.

1. AI Triage Processing
2. PACS Worklist Experience
3. Reading Experience
4. Feedback Capture

The workflow begins immediately after a CT Brain study is acquired and ends when the radiologist confirms or overrides the AI recommendation.

---

## 8.1 End-to-End Workflow

The product shall support the following workflow:

1. A new CT Brain study is acquired.
2. The study is automatically sent to the AI Triage Engine.
3. AI analyses the complete CT study.
4. The AI predicts whether Intracranial Hemorrhage (ICH) is suspected.
5. A confidence score is generated.
6. The study priority is automatically updated.
7. The worklist refreshes without user intervention.
8. The radiologist opens the study.
9. AI findings are displayed alongside the CT images.
10. The radiologist reviews the study and records the final clinical decision.
11. Radiologist feedback is stored for future model improvement.

---

# 8.2 AI Triage Processing

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| AI-01 | The system shall automatically analyse every newly acquired CT Brain study without user intervention. | Must |
| AI-02 | The system shall predict whether intracranial hemorrhage is suspected. | Must |
| AI-03 | The system shall generate a confidence score for every prediction. | Must |
| AI-04 | The system shall assign a worklist priority based on the prediction and confidence level. | Must |
| AI-05 | The system shall complete analysis before updating the worklist. | Must |

### Business Rules

- AI processing begins automatically after image acquisition.
- Every study receives exactly one prediction.
- Every prediction includes a confidence score.
- AI does not make the clinical diagnosis.
- Priority assignment follows the product prioritization policy.

### Acceptance Criteria

- AI processing starts automatically for every new study.
- Every processed study receives a prediction.
- Every prediction includes a confidence value.
- Worklist priority updates only after AI processing is complete.

---

# 8.3 PACS Worklist Experience

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| WL-01 | The worklist shall display all available CT Brain studies. | Must |
| WL-02 | The worklist shall display AI processing status for newly received studies. | Must |
| WL-03 | The worklist shall automatically reorder studies after AI processing completes. | Must |
| WL-04 | The worklist shall display a visual priority indicator for every completed study. | Must |
| WL-05 | Users shall be able to open any study directly from the worklist. | Must |

### Business Rules

- Newly received studies initially display an **AI Processing** status.
- Priority updates occur automatically.
- High-priority studies appear above lower-priority studies.
- Manual sorting is outside the MVP scope.

### Acceptance Criteria

- New studies appear immediately after acquisition.
- Worklist updates automatically without requiring page refresh.
- High-priority studies move to the correct position.
- Selecting a study opens the Reading Experience.

---

# 8.4 Reading Experience

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| RD-01 | The system shall display the CT study selected from the worklist. | Must |
| RD-02 | The system shall display the AI prediction. | Must |
| RD-03 | The system shall display the AI confidence score. | Must |
| RD-04 | The system shall display explainability information highlighting suspected regions. | Should |
| RD-05 | The radiologist shall be able to confirm or override the AI recommendation. | Must |

### Business Rules

- AI findings are presented as decision support only.
- Confidence information is always displayed together with the prediction.
- Explainability information supports interpretation but is not mandatory for diagnosis.
- Final diagnosis remains the responsibility of the radiologist.

### Acceptance Criteria

- The selected CT study loads successfully.
- AI prediction and confidence are visible.
- Radiologist actions are available.
- Override actions do not require restarting AI analysis.

---

# 8.5 Feedback Capture

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FB-01 | The system shall record the radiologist's final decision. | Must |
| FB-02 | The system shall record AI predictions for comparison. | Must |
| FB-03 | The system shall store override actions for future analysis. | Should |
| FB-04 | The system shall support future model improvement using captured feedback. | Could |

### Business Rules

- Feedback collection does not interrupt clinical workflow.
- Feedback is associated with the corresponding AI prediction.
- Captured feedback is used for continuous product improvement.

### Acceptance Criteria

- Radiologist feedback is successfully recorded.
- AI prediction and final decision are linked.
- Override actions are available for later review.

---

# 9. Non-Functional Requirements

The following non-functional requirements define the expected quality attributes of NeuroTriage AI.

| Category | Requirement |
|----------|-------------|
| Performance | AI analysis should complete within the target inference time defined in the Evaluation Strategy. |
| Reliability | The product shall continue to function reliably during continuous emergency department operation. |
| Availability | The system should remain available throughout routine clinical operations with minimal downtime. |
| Usability | AI recommendations shall be presented in a simple, intuitive manner requiring minimal additional user interaction. |
| Explainability | Every AI prediction shall be accompanied by confidence information and explainability support. |
| Security | Patient information shall be protected through anonymization and secure data handling practices. |
| Scalability | The product shall support deployment across multiple hospitals without requiring changes to core functionality. |
| Maintainability | AI models and software components shall support future updates without disrupting existing workflows. |

---

# 10. User Stories

### US-01

**As a** Radiologist  
**I want** newly acquired CT brain studies to be analysed automatically  
**So that** emergency cases are identified without manual intervention.

---

### US-02

**As a** Radiologist  
**I want** suspected intracranial hemorrhage cases to appear higher in my worklist  
**So that** I can review critical patients earlier.

---

### US-03

**As a** Radiologist  
**I want** every AI prediction to include a confidence score  
**So that** I can better judge the reliability of the recommendation.

---

### US-04

**As a** Radiologist  
**I want** to view AI explainability information alongside the CT images  
**So that** I understand why the AI reached its prediction.

---

### US-05

**As a** Radiologist  
**I want** to confirm or override the AI recommendation  
**So that** final clinical responsibility remains under my control.

---

### US-06

**As a** Hospital Administrator  
**I want** the product to integrate with existing radiology workflows  
**So that** productivity improves without disrupting current clinical practice.

---

### US-07

**As a** Product Manager  
**I want** radiologist feedback to be captured  
**So that** future versions of the AI can continuously improve.

---

# 11. MVP Scope

The MVP demonstrates the core value proposition of NeuroTriage AI by simulating an AI-assisted emergency radiology workflow.

### Included

- PACS worklist simulation
- Automatic AI processing of incoming CT Brain studies
- AI-assisted worklist prioritization
- Reading screen with CT image viewer
- AI prediction and confidence display
- Explainability visualization
- Radiologist confirmation or override
- Feedback capture

### Excluded

The following capabilities are intentionally excluded from the MVP:

- Hospital authentication and user management
- Live PACS integration
- DICOM networking
- Multi-user collaboration
- Clinical report generation
- Regulatory workflows
- Production deployment infrastructure

---

# 12. Assumptions and Dependencies

## Assumptions

- CT Brain studies are available immediately after image acquisition.
- AI inference is completed before worklist prioritization.
- Radiologists remain the final decision makers.
- The AI model has been clinically validated before deployment.

---

## Dependencies

The successful implementation of NeuroTriage AI depends on:

- Availability of anonymized CT Brain datasets
- AI inference service
- Existing PACS workflow
- Clinical validation by expert radiologists
- Product approval by hospital stakeholders

---

# 13. Product Risks

| Risk | Potential Impact | Mitigation |
|------|------------------|------------|
| Missed ICH (False Negative) | Delayed diagnosis of critical patients | Human-in-the-Loop review and conservative prioritization policy |
| Over-reliance on AI | Reduced clinical vigilance | Confidence scores, explainability, and clinician override |
| Workflow Disruption | Reduced clinician adoption | Pilot deployment and gradual rollout |
| Model Performance Drift | Reduced long-term accuracy | Continuous monitoring and periodic model updates |

Detailed governance controls are documented in the **Ethics, Governance, and Risk Note**.

---

# 14. Future Enhancements

The MVP establishes the foundation for AI-assisted emergency stroke triage. Future product releases will expand the platform while preserving the core product principles of patient safety, clinician trust, and seamless workflow integration.

## Phase 2 – Clinical Expansion

Future enhancements may include:

- Support for additional neurological emergencies such as ischemic stroke and brain tumors.
- Enhanced explainability visualizations to improve clinician confidence.
- Feedback-driven model improvement using validated clinical outcomes.
- Workflow analytics dashboard for monitoring operational efficiency.

---

## Phase 3 – Enterprise Platform

Long-term product evolution may include:

- Multi-condition AI detection within a single workflow.
- AI-assisted preliminary reporting to support radiologist productivity.
- Multi-hospital deployment with centralized model management.
- Continuous performance monitoring and governance dashboards.

---

# 15. Requirements Traceability Matrix

The following matrix demonstrates how the major product requirements map to business objectives and user-facing functionality.

| Requirement | Product Objective | Prototype Component |
|-------------|------------------|---------------------|
| Automatic AI analysis of incoming CT studies | Reduce time to identify emergency cases | AI Processing |
| Dynamic worklist prioritization | Improve emergency workflow efficiency | PACS Worklist |
| AI confidence display | Increase clinician trust | Reading Screen |
| Explainability support | Improve transparency of AI recommendations | Reading Screen |
| Radiologist confirmation and override | Maintain clinician control | Reading Screen |
| Feedback capture | Support continuous product improvement | Feedback Module |

This traceability ensures that every major product capability contributes directly to the overall business and clinical objectives.

---

# 16. Glossary

| Term | Description |
|------|-------------|
| AI | Artificial Intelligence |
| ICH | Intracranial Hemorrhage |
| PACS | Picture Archiving and Communication System |
| CT | Computed Tomography |
| ROI | Region of Interest |
| MVP | Minimum Viable Product |
| Human-in-the-Loop | Workflow in which the radiologist remains responsible for the final clinical decision while AI provides decision support. |

---

# 17. Document Approval

This Product Requirements Document represents the agreed product scope and behaviour for Version 1.0 of NeuroTriage AI.

Any future changes to product functionality should be evaluated against the product principles defined in this document to ensure continued alignment with the overall vision, user needs, and business objectives.

---

# End of Document
