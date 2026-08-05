import os
from pathlib import Path
from uuid import uuid4
from datetime import datetime


import joblib
import pandas as pd
from pyspark.errors import AnalysisException
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import (
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)
from sklearn.preprocessing import LabelEncoder

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "models" / "fraud_detection_model.pkl"

os.environ.setdefault("SPARK_LOCAL_HOSTNAME", "localhost")

# Only set HADOOP_HOME when winutils is truly present. A bad path here can make the
# local filesystem or checkpoint setup behave unpredictably on Windows.
hadoop_home = os.environ.get("HADOOP_HOME") or r"C:\hadoop"
if hadoop_home and os.path.exists(hadoop_home):
    os.environ["HADOOP_HOME"] = hadoop_home
    os.environ["hadoop.home.dir"] = hadoop_home
    hadoop_bin = Path(hadoop_home) / "bin"
    if hadoop_bin.exists():
        os.environ["PATH"] = os.pathsep.join(
            filter(None, [str(hadoop_bin), os.environ.get("PATH", "")])
        )

# Spark Structured Streaming with Kafka requires the connector jar at runtime.
# Without it, Spark raises: 'Failed to find data source: kafka'.
# Keep this explicit so startup fails clearly and with a known package name.
SPARK_PACKAGES = (
    "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.9,"
    "com.datastax.spark:spark-cassandra-connector_2.12:3.5.0"
)

spark_builder = (
    SparkSession.builder
    .appName("RealTimeFraudDetection")
    .master("local[*]")
    .config("spark.driver.host", "localhost")
    .config("spark.driver.bindAddress", "localhost")
    .config("spark.driver.port", "4040")
    .config("spark.blockManager.port", "4041")
    .config("spark.sql.shuffle.partitions", "1")
    .config("spark.hadoop.io.nativeio.enabled", "false")
    .config("spark.hadoop.fs.defaultFS", "file:///")
    .config(
        "spark.hadoop.fs.file.impl",
        "org.apache.hadoop.fs.LocalFileSystem"
    )
    .config(
        "spark.hadoop.fs.AbstractFileSystem.file.impl",
        "org.apache.hadoop.fs.local.LocalFs"
    )
    .config(
        "spark.sql.warehouse.dir",
        str((PROJECT_ROOT / "tmp" / "spark-warehouse").resolve())
    )
    .config("spark.jars.packages", SPARK_PACKAGES)
)

spark_builder = (
    spark_builder
    .config(
        "spark.executorEnv.PYSPARK_PYTHON",
        r"C:\Users\Suji\Desktop\Real-Time-Financial-Fraud-Detection-Pipeline\.venv311\Scripts\python.exe"
    )
    .config(
        "spark.pyspark.python",
        r"C:\Users\Suji\Desktop\Real-Time-Financial-Fraud-Detection-Pipeline\.venv311\Scripts\python.exe"
    )
)

spark = spark_builder.getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

if not MODEL_PATH.exists():
    raise FileNotFoundError(f"Model not found at: {MODEL_PATH}")

model = joblib.load(MODEL_PATH)


def load_label_encoder():
    candidates = [
        PROJECT_ROOT / "models" / "label_encoder.pkl",
        PROJECT_ROOT / "models" / "label_encoders.pkl",
    ]

    for path in candidates:
        if not path.exists():
            continue

        obj = joblib.load(path)
        if isinstance(obj, dict):
            if "type" in obj:
                return obj["type"]
            if obj:
                return next(iter(obj.values()))
        return obj

    encoder = LabelEncoder()
    encoder.fit(["CASH_IN", "CASH_OUT", "DEBIT", "PAYMENT", "TRANSFER"])
    return encoder


label_encoder = load_label_encoder()

schema = StructType([
    StructField("step", IntegerType(), True),
    StructField("type", StringType(), True),
    StructField("amount", DoubleType(), True),
    StructField("oldbalanceOrg", DoubleType(), True),
    StructField("newbalanceOrig", DoubleType(), True),
    StructField("oldbalanceDest", DoubleType(), True),
    StructField("newbalanceDest", DoubleType(), True),
    StructField("isFlaggedFraud", IntegerType(), True),
])

try:
    kafka_df = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", "localhost:9092")
        .option("subscribe", "transactions")
        .option("startingOffsets", "latest")
        .option("failOnDataLoss", "false")
        .load()
    )
except AnalysisException as exc:
    if "Failed to find data source: kafka" in str(exc):
        raise RuntimeError(
            "Kafka datasource jar not found in Spark runtime. Install the connector jar "
            "with the package 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.9' "
            "or run Spark with --packages and ensure Maven connectivity is available."
        ) from exc
    raise

transactions_df = (
    kafka_df
    .select(from_json(col("value").cast("string"), schema).alias("data"))
    .select("data.*")
)


def predict_fraud(batch_df, batch_id):
    if batch_df.count() == 0:
        return

    pandas_df = batch_df.toPandas().copy()

    if "type" in pandas_df.columns:
        pandas_df["type"] = pandas_df["type"].astype(str).str.upper()
        pandas_df["type"] = label_encoder.transform(pandas_df["type"])

    cols = [
        "step",
        "type",
        "amount",
        "oldbalanceOrg",
        "newbalanceOrig",
        "oldbalanceDest",
        "newbalanceDest",
        "isFlaggedFraud",
    ]
    features = pandas_df[cols]
    pred = model.predict(features)
    pandas_df["prediction"] = pred.astype(int)
    pandas_df["id"] = [str(uuid4()) for _ in range(len(pandas_df))]
    pandas_df["timestamp"] = str(datetime.now())

    from pyspark.sql.types import (
        StructType,
        StructField,
        StringType,
        DoubleType,
        IntegerType
    )


    output_schema = StructType([
        StructField("id", StringType(), True),
        StructField("amount", DoubleType(), True),
        StructField("type", IntegerType(), True),
        StructField("prediction", IntegerType(), True),
        StructField("timestamp", StringType(), True)
    ])


    output_df = spark.createDataFrame(
        pandas_df[
            [
                "id",
                "amount",
                "type",
                "prediction",
                "timestamp"
            ]
        ],
        schema=output_schema
    )

    output_df.write \
        .format("org.apache.spark.sql.cassandra") \
        .mode("append") \
        .options(
            keyspace="fraud_detection",
            table="transactions"
        ) \
        .save()

    print(
        pandas_df[
            [
                "amount",
                "type",
                "prediction"
            ]
        ]
    )


CHECKPOINT_DIR = PROJECT_ROOT / "checkpoint"
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

CHECKPOINT_PATH = (
    "file:///"
    + str(CHECKPOINT_DIR.resolve()).replace("\\", "/")
)


query = (
    transactions_df
    .writeStream
    .foreachBatch(predict_fraud)
    .outputMode("append")
    .option(
        "checkpointLocation",
        CHECKPOINT_PATH
    )
    .start()
)

print("Real-Time Fraud Detection Streaming Started...")

query.awaitTermination()