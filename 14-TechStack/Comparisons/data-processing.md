# Data Processing: Dataflow vs Spark vs Airflow
- Dataflow: managed Beam, streaming/batch, autoscale.
- Spark: rich ecosystem, may run on k8s/EMR/Dataproc.
- Airflow: orchestration, not processing engine.
- Decision: need orchestration? Airflow; need managed streaming? Dataflow; need custom libs/ecosystem? Spark.
