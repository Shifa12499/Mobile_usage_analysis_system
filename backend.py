from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pyspark.sql import SparkSession
from pyspark.sql.functions import sum as _sum, desc
import os
import sys

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Spark session (created lazily)
spark = None

def get_spark_session():
    global spark
    if spark is None:
        try:
            # Set JAVA_HOME if not already set (Windows fix)
            if not os.environ.get('JAVA_HOME'):
                # Try common Java installation paths on Windows
                java_paths = [
                    r"C:\Program Files\Eclipse Adoptium\jdk-8.0.472.8-hotspot",
                    r"C:\Program Files\Java\jdk1.8.0_472",
                    r"C:\Program Files\Java\jdk-8",
                    r"C:\Program Files\OpenJDK\jdk-8"
                ]
                
                for path in java_paths:
                    if os.path.exists(path):
                        os.environ['JAVA_HOME'] = path
                        print(f"✅ Set JAVA_HOME to: {path}")
                        break
            
            # FIXED: Spark session that works on Windows (no Hadoop needed)
            spark = SparkSession.builder \
                .appName("MobileUsageAnalysis") \
                .master("local[*]") \
                .config("spark.driver.bindAddress", "127.0.0.1") \
                .config("spark.ui.enabled", "false") \
                .getOrCreate()
            
            spark.sparkContext.setLogLevel("ERROR")
            print("✅ Spark session created successfully!")
        except Exception as e:
            print(f"❌ Error creating Spark session: {e}")
            print("\n⚠️  Java is required for PySpark. Please install Java JDK 8 or 11.")
            print("Download from: https://adoptium.net/")
            raise
    return spark

@app.post("/analyze")
async def analyze_csv(file: UploadFile = File(...)):
    # Get or create Spark session
    spark = get_spark_session()
    
    contents = await file.read()

    with open("uploaded.csv", "wb") as f:
        f.write(contents)

    # Read CSV with Spark
    df = spark.read.csv("uploaded.csv", header=True, inferSchema=True)
    
    print("=" * 50)
    print("SPARK DATAFRAME SCHEMA:")
    df.printSchema()
    print("\nSpark DataFrame Count:", df.count())
    print("\nSample Data:")
    df.show()
    print("=" * 50)

    # Calculate total usage using Spark aggregation
    total_usage = df.agg(_sum("usage_minutes").alias("total")).collect()[0]["total"]
    print(f"Total Usage (Spark): {total_usage} minutes")

    # Find most used app using Spark groupBy
    top_app_df = df.groupBy("app_name") \
                   .agg(_sum("usage_minutes").alias("total")) \
                   .orderBy(desc("total"))
    
    print("\nTop Apps (Spark):")
    top_app_df.show()
    
    top_app = top_app_df.first()["app_name"]
    print(f"Most Used App: {top_app}")

    # Find peak hour using Spark groupBy
    peak_hour_df = df.groupBy("hour") \
                     .agg(_sum("usage_minutes").alias("total")) \
                     .orderBy(desc("total"))
    
    print("\nPeak Hours (Spark):")
    peak_hour_df.show()
    
    peak_hour = peak_hour_df.first()["hour"]
    print(f"Peak Hour: {peak_hour}")

    # Get app-wise usage for chart
    app_usage_df = df.groupBy("app_name") \
                     .agg(_sum("usage_minutes").alias("total")) \
                     .orderBy(desc("total"))

    app_usage = [{"app": row["app_name"], "minutes": int(row["total"])}
                 for row in app_usage_df.collect()]
    
    print("\nApp Usage Summary:")
    for app in app_usage:
        print(f"  {app['app']}: {app['minutes']} minutes")
    print("=" * 50)

    result = {
        "total_usage_minutes": int(total_usage) if total_usage else 0,
        "most_used_app": str(top_app),
        "peak_usage_hour": str(peak_hour),
        "app_usage": app_usage
    }
    
    # Cleanup uploaded file
    if os.path.exists("uploaded.csv"):
        os.remove("uploaded.csv")
    
    return result

@app.get("/")
async def root():
    return {"message": "Mobile Usage Analysis API with PySpark", "status": "running"}
