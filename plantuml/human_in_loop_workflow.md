@startuml
title Human-in-the-Loop Review

start

:AI analyzes CT Study;

:Generate Prediction;

:Generate Confidence Score;

:Display Recommendation;

:Radiologist Reviews;

if (Accept AI?) then (Yes)

:Confirm Diagnosis;

else (No)

:Override AI Recommendation;

endif

:Capture Feedback;

:Store for Model Improvement;

stop
@enduml
