# Prototype / MVP

## Prototype Type

**Web application / browser-based interactive prototype** built with React/TypeScript and a Python backend. The prototype uses real anonymized CT DICOM studies with a simulated AI inference layer.

## What It Demonstrates

The prototype demonstrates the end-to-end NeuroTriage AI workflow:

**CT study arrives → AI processing → priority assignment → reprioritized worklist → radiologist review → AI finding/overlay → confirm or override → feedback recorded**

It also demonstrates:
- Staged arrival of new CT studies
- Critical / High / Moderate / Routine prioritization
- Brain and Blood/ICH CT window presets
- Jump-to-Finding navigation
- AI overlay aligned with the identified finding
- Human confirmation or override
- Reset Demo to restore the clean demonstration state

## AI Role

AI creates value by analysing the CT study and providing a **finding assessment, confidence level, and urgency priority**. These outputs are used to reprioritize the radiologist's worklist so that potentially critical cases can be reviewed earlier.

For the academic prototype, AI inference is simulated. The architecture is designed so that a validated clinical AI inference service can replace the simulated component in a future implementation.

## What It Does Not Yet Prove

The prototype does **not** prove clinical AI accuracy, clinical safety, regulatory readiness, production-scale performance, or live PACS integration.

It demonstrates the **workflow and product concept**, using real anonymized CT images, rather than validating a clinical AI model.

## Links

- Repository: Accompanying GitHub repository
- Live Demo: `http://localhost:5173/` (local demo)
- Video: https://youtu.be/I6gwdCbi2uo
