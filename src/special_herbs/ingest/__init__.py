"""Substrate-side data ingestion.

Per ADR-0001 §4, the substrate ingests upstream sources independently —
no shared databases with consumers. Each Volume's training pipeline
declares its own ingestion modules here.
"""
