# Data and artifacts

## Datasets (not redistributed)

- **CICIDS2017**: Canadian Institute for Cybersecurity, University of New Brunswick (Sharafaldin et al., ICISSP 2018).
- **CSE-CIC-IDS2018**: Communications Security Establishment and Canadian Institute for Cybersecurity.

Both datasets have documented labelling and feature-generation issues (Engelen et al., IEEE SPW 2021; Liu et al., IEEE CNS 2022). Use the original CICFlowMeter CSV releases so that results match.

## Partitions

The clean CICIDS2017 population (2,747,873 flows) was split group-disjointly into training (1,648,724), validation (412,181), calibration (274,787) and IID-test (412,181) partitions. A group is the set of flows with an identical 76-feature vector, identified by a stable 64-bit hash. The clean population forms 2,233,419 groups, and no group crosses partitions (`artifacts/metadata/TrustShift_IDS_STEP_4_FROZEN_SUMMARY.json`; split SHA-256 `62e60eb5…de1408`). The ambiguity-stress population (82,870 flows) is held out from all partitions.

## What goes where

| Item | GitHub | Zenodo |
|---|---|---|
| Code, notebooks, window-level CSV results, figures | yes | yes (release snapshot) |
| Frozen models (2.5 MB), S3 masks, medians and V1 metadata (`models/`, `artifacts/`) | yes (included) | yes |
| Stream and compound feature NPZ files (hundreds of MB) | no | yes |
| CSE-CIC-IDS2018 prediction shards (GB) | no | yes, or regenerate with notebook 01 |
| Processed parquet partitions (GB) | no | no (regenerate from the raw datasets) |
