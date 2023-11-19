import findspark
findspark.init()
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType,BooleanType, IntegerType, ArrayType, FloatType

SparkSession.builder.config(conf=SparkConf())

spark = SparkSession.builder \
    .appName("KafkaSparkIntegration") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.4,"
            "org.elasticsearch:elasticsearch-spark-30_2.12:8.11.0") \
    .getOrCreate()

# Read data from Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "movie_recommendation") \
    .option("startingOffsets", "earliest") \
    .load()

# Schema definition
schema = StructType([
    StructField("adult", BooleanType(), True),
    StructField("backdrop_path", StringType(), True),
    StructField("belongs_to_collection", StructType([
        StructField("id", IntegerType(), True),
        StructField("name", StringType(), True),
        StructField("poster_path", StringType(), True),
        StructField("backdrop_path", StringType(), True)
    ]), True),
    StructField("budget", IntegerType(), True),
    StructField("genres", ArrayType(StructType([
        StructField("id", IntegerType(), True),
        StructField("name", StringType(), True)
    ])), True),
    StructField("homepage", StringType(), True),
    StructField("id", IntegerType(), True),
    StructField("imdb_id", StringType(), True),
    StructField("original_language", StringType(), True),
    StructField("original_title", StringType(), True),
    StructField("overview", StringType(), True),
    StructField("popularity", FloatType(), True),
    StructField("poster_path", StringType(), True),
    StructField("production_companies", ArrayType(StructType([
        StructField("id", IntegerType(), True),
        StructField("logo_path", StringType(), True),
        StructField("name", StringType(), True),
        StructField("origin_country", StringType(), True)
    ])), True),
    StructField("production_countries", ArrayType(StructType([
        StructField("iso_3166_1", StringType(), True),
        StructField("name", StringType(), True)
    ])), True),
    StructField("release_date", StringType(), True),
    StructField("revenue", FloatType(), True),
    StructField("runtime", IntegerType(), True),
    StructField("spoken_languages", ArrayType(StructType([
        StructField("english_name", StringType(), True),
        StructField("iso_639_1", StringType(), True),
        StructField("name", StringType(), True)
    ])), True),
    StructField("status", StringType(), True),
    StructField("tagline", StringType(), True),
    StructField("title", StringType(), True),
    StructField("video", BooleanType(), True),
    StructField("vote_average", FloatType(), True),
    StructField("vote_count", IntegerType(), True)
])



value_df = df.selectExpr("CAST(value AS STRING)")

# Apply schema to parse JSON data
selected_df = value_df.withColumn("values", F.from_json(value_df["value"], schema)).selectExpr("values")

# result_df = selected_df.withColumn("release_date", F.to_date("release_date"))
# result_df = result_df.withColumn("description", F.concat_ws(" - ", F.col("title"), F.col("overview")))


# Selecting required columns for visualizations
result_df = selected_df.select(
    F.col("values.adult").alias("adult"),
    F.col("values.belongs_to_collection").alias("belongs_to_collection"),
    F.col("values.belongs_to_collection.name").alias("name_collection"),
    F.col("values.budget").alias("budget"),
    F.col("values.genres.id").alias("genre_id"),
    F.col("values.genres.name").alias("genres_name"),
    F.col("values.original_language").alias("original_language"),
    F.col("values.overview").alias("overview"),
    F.col("values.popularity").alias("popularity"), 
    F.col("values.production_companies.name").alias("name_production_company"),
    F.col("values.status").alias("status"),
    F.col("values.production_companies.id").alias("id_production_company"),   
    F.col("values.production_companies.origin_country").alias("origin_country_production_company"),
    F.col("values.production_countries.name").alias("name_production_countries"),  
    F.col("values.release_date").alias("release_date"),
    F.col("values.revenue").alias("revenue"),
    F.col("values.tagline").alias("tagline"),
    F.col("values.title").alias("title"),
    F.col("values.video").alias("video"),
    F.col("values.vote_average").alias("vote_average"),
    F.col("values.vote_count").alias("vote_count"),
    # F.col("description"),
)

# Elasticsearch index mapping definition
# mapping = {
#     "mappings": {
#         "properties": {
#             "adult": {"type": "boolean"},
#             "backdrop_path": {"type": "text"},
#             "belongs_to_collection": {
#                 "properties": {
#                     "id": {"type": "integer"},
#                     "name": {"type": "text"},
#                     "poster_path": {"type": "text"},
#                     "backdrop_path": {"type": "text"}
#                 }
#             },
#             "budget": {"type": "integer"},
#             "genres": {
#                 "type": "nested",
#                 "properties": {
#                     "id": {"type": "integer"},
#                     "name": {"type": "text"}
#                 }
#             },
#             "homepage": {"type": "text"},
#             "id": {"type": "integer"},
#             "imdb_id": {"type": "text"},
#             "original_language": {"type": "text"},
#             "original_title": {"type": "text"},
#             "overview": {"type": "text"},
#             "popularity": {"type": "float"},
#             "poster_path": {"type": "text"},
#             "production_companies": {
#                 "type": "nested",
#                 "properties": {
#                     "id": {"type": "integer"},
#                     "logo_path": {"type": "text"},
#                     "name": {"type": "text"},
#                     "origin_country": {"type": "text"}
#                 }
#             },
#             "production_countries": {
#                 "type": "nested",
#                 "properties": {
#                     "iso_3166_1": {"type": "text"},
#                     "name": {"type": "text"}
#                 }
#             },
#             "release_date": {"type": "date", "format": "yyyy-MM-dd"},
#             "revenue": {"type": "float"},
#             "runtime": {"type": "integer"},
#             "spoken_languages": {
#                 "type": "nested",
#                 "properties": {
#                     "english_name": {"type": "text"},
#                     "iso_639_1": {"type": "text"},
#                     "name": {"type": "text"}
#                 }
#             },
#             "status": {"type": "text"},
#             "tagline": {"type": "text"},
#             "title": {"type": "text"},
#             "video": {"type": "boolean"},
#             "vote_average": {"type": "float"},
#             "vote_count": {"type": "integer"}
#             # Include other fields if present in your data
#         }
#     }
# }
query = result_df.writeStream \
    .format("org.elasticsearch.spark.sql") \
    .outputMode("append") \
    .option("es.resource", "moviedb_data") \
    .option("es.nodes", "localhost") \
    .option("es.port", "9200") \
    .option("es.nodes.wan.only", "true")\
    .option("es.index.auto.create", "true")\
    .option("checkpointLocation", "./data/elasticsearch/") \
    .start()

query = result_df.writeStream.outputMode("append").format("console").start()

query.awaitTermination()