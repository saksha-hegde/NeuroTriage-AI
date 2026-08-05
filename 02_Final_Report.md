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

# Product Strategy

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

> *Copy the complete contents of `PM_Artifact_Pack.md` here.*

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
