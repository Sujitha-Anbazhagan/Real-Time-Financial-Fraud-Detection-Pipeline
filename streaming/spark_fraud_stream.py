import os
import joblib
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import (
    StructType, StructField, IntegerType, StringType, DoubleType
)
from sklearn.preprocessing import LabelEncoder

os.environ["SPARK_LOCAL_HOSTNAME"] = "localhost"

# Spark 3.5.9 on Windows requires a valid Hadoop home when creating local filesystem
# checkpoint metadata. Keep the environment set; do not unset it at runtime.
hadoop_home = os.environ.get("HADOOP_HOME") or r"C:\hadoop"
if os.path.exists(hadoop_home):
    os.environ["HADOOP_HOME"] = hadoop_home
    os.environ["hadoop.home.dir"] = hadoop_home
    os.environ["PATH"] = os.pathsep.join(
        filter(None, [os.path.join(hadoop_home, "bin"), os.environ.get("PATH", "")])
    )

spark = (
    SparkSession.builder
    .appName("RealTimeFraudDetection")
    .master("local[*]")
    .config("spark.driver.host", "127.0.0.1")
    .config("spark.driver.bindAddress", "127.0.0.1")
    .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", "true")
    .config("spark.hadoop.io.nativeio.enabled", "false")
    .config("spark.hadoop.fs.file.impl", "org.apache.hadoop.fs.LocalFileSystem")
    .config("spark.hadoop.fs.defaultFS", "file:///")
    .config("spark.sql.shuffle.io.enabled", "false")
    .config("spark.sql.warehouse.dir", "file:///C:/tmp/spark-warehouse")
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.9")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("ERROR")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "fraud_detection_model.pkl")

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model not found at: {MODEL_PATH}")

model = joblib.load(MODEL_PATH)

def load_label_encoder():
    encoder_candidates = [
        os.path.join(BASE_DIR, "models", "label_encoder.pkl"),
        os.path.join(BASE_DIR, "models", "label_encoders.pkl"),
    ]
    for path in encoder_candidates:
        if os.path.exists(path):
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

kafka_df = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "localhost:9092")
    .option("subscribe", "transactions")
    .option("startingOffsets", "earliest")
    .load()
)

transactions_df = (
    kafka_df
    .select(from_json(col("value").cast("string"), schema).alias("data"))
    .select("data.*")
)

def predict_fraud(batch_df, batch_id):
    if batch_df.count() > 0:
        pandas_df = batch_df.toPandas().copy()
        if "type" in pandas_df.columns and not pd.api.types.is_numeric_dtype(pandas_df["type"]):
            pandas_df["type"] = pandas_df["type"].astype(str).str.upper()
            pandas_df["type"] = label_encoder.transform(pandas_df["type"])

        cols = [
            "step", "type", "amount", "oldbalanceOrg",
            "newbalanceOrig", "oldbalanceDest", "newbalanceDest", "isFlaggedFraud"
        ]
        features = pandas_df[cols]
        pred = model.predict(features)
        pandas_df["prediction"] = pred.astype(int)
        print(pandas_df[["amount", "type", "prediction"]])

# Use a workspace-local checkpoint directory so it is clearly writable on Windows.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECKPOINT_DIR = os.path.join(BASE_DIR, "tmp", "fraud_stream_checkpoint")
os.makedirs(CHECKPOINT_DIR, exist_ok=True)
CHECKPOINT_PATH = "file:///C:/tmp/fraud_stream_checkpoint"
query = (
    transactions_df
    .writeStream
    .foreachBatch(predict_fraud)
    .outputMode("append")
    .option("checkpointLocation", CHECKPOINT_PATH)
    .start()
)

print("Real-Time Fraud Detection Streaming Started...")
query.awaitTermination()