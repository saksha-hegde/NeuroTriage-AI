"""
Application configuration.

Kept as plain constants (not pydantic-settings) to avoid an extra dependency for
an MVP prototype. Values that clinical/product stakeholders may want to tune
(timing, confidence thresholds) live here so they are easy to find and change
without hunting through business logic.
"""

APP_NAME = "NeuroTriage AI - Prototype API"
APP_VERSION = "0.1.0"

# Origins allowed to call this API. The Vite dev server's default port.
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# --- Simulated study workflow timing (seconds) -----------------------------
# How long a newly "simulated" study spends in each status before advancing.
# Tuned so a live demo feels real without making an audience wait.
STUDY_ACQUIRING_SECONDS = 2.0
STUDY_AI_PROCESSING_SECONDS = 3.0

# --- Prioritization policy ---------------------------------------------------
# Confidence is a 0-1 probability. The UX Workflow & Trust Design doc's policy
# table defines exactly two confidence tiers - High and Medium - so routing
# uses a single boundary. The exact number isn't specified in the product
# docs, so it's a named, adjustable constant rather than buried in logic.
# See app/core/prioritization.py for how the tier combines with the AI
# assessment to produce a priority.
CONFIDENCE_HIGH_THRESHOLD = 0.80  # >= this is "High" confidence, else "Medium"

# Per the "Patient Safety First" product principle (favour earlier human
# review under uncertainty), confidence below this floor is still bucketed as
# "Medium" (not deprioritized further) - it exists only to flag unusually low
# confidence for logging/monitoring, not to change routing.
CONFIDENCE_LOW_WARNING_THRESHOLD = 0.50
