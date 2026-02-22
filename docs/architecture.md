# Architecture Overview

## System Style

Orchestration Layer + Distributed Model Services + Ensemble Fusion Engine.

## Core Layers

1. API Gateway
- JWT auth and OAuth2 token issuance
- payload/rate/exception/request middleware
- validation, routing, orchestration
- history and forensic logging

2. Distributed Model Services
- isolated FastAPI services
- `/predict` contract returns probability, class, and latency
- timeout-controlled requests from gateway

3. Ensemble Engine
- strategies: voting, averaging, stacking
- startup artifact loading:
  - `deepsafe_meta_learner.joblib`
  - `deepsafe_meta_scaler.joblib`
  - `deepsafe_meta_imputer.joblib`
  - `feature_columns.json`
- deterministic binary verdict via threshold logic

## Duplicate Prevention

- SHA-256 fingerprint generated from uploaded bytes
- existing hash returns cached verdict and skips inference

## Innovation Principles

- Microservice-based model isolation
- Stacking ensemble meta-learning
- Config-driven model registry
- Deterministic binary classification
- Forensic-grade logging and audit trails
- Multimodal extensibility
