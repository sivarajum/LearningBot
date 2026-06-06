# GCP Storage: BQ vs Spanner vs Cloud SQL vs Firestore vs Bigtable
- BQ: analytics, columnar, petabyte-scale.
- Spanner: global relational, strong consistency.
- Cloud SQL: managed RDBMS, zonal/regional.
- Firestore: doc store, flexible schema.
- Bigtable: wide-column, low-latency, time-series.
- Decision: analytics -> BQ; global relational -> Spanner; transactional standard -> SQL; flexible doc/mobile -> Firestore; low-latency/ts -> Bigtable.
