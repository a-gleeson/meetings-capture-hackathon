import os

from dotenv import find_dotenv, load_dotenv

_ = load_dotenv(find_dotenv())

LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")

PROJECT_PATH = os.environ.get("PROJECT_PATH")
OPENSEARCH_URL = os.environ.get("OPENSEARCH_URL")
OPENSEARCH_BATCH_SIZE = int(os.environ.get("OPENSEARCH_BATCH_SIZE", 500))
OPENSEARCH_ENDPOINT_NAME = os.environ.get(
    "OPENSEARCH_ENDPOINT_NAME", "vstore"
)
OPENSEARCH_INDEX_NAME = os.environ.get("OPENSEARCH_INDEX_NAME", "vacancies")
OPENSEARCH_SKILLS_INDEX_NAME = os.environ.get(
    "OPENSEARCH_SKILLS_INDEX_NAME", "unique_skills"
)
EMBEDDING_ENDPOINT_NAME = os.environ.get(
    "EMBEDDING_ENDPOINT_NAME", "huggingface-sentencesimilarity"
)

S3_LOADER_BUCKET = os.environ.get("S3_LOADER_BUCKET", "rcp")
S3_LOADER_FILE_NAME = os.environ.get(
    "S3_LOADER_FILE_NAME", "all_data_null_test_2.parquet"
)
AWS_REGION = os.environ.get("AWS_REGION", "eu-west-2")
ENV = os.environ.get("ENV", "prod")


LOADER_CONFIG = os.environ.get("LOADER_CONFIG", "s3_loader")  # "file_loader"
VECTOR_STORE_CONFIG = os.environ.get(
    "VECTOR_STORE_CONFIG", "opensearch"
)  # "chroma""opensearch"
LLM_MODEL = os.environ.get("LLM_MODEL", "hosted_llm")  # "local_llm"

AWS_REGION = os.environ.get("AWS_REGION", "eu-west-2")
AWS_SERVICE_ROLE_ARN = os.environ.get("AWS_SERVICE_ROLE_ARN", "arn:aws:iam::")
AWS_SAGEMAKER_ENDPOINT = os.environ.get(
    "AWS_SAGEMAKER_ENDPOINT", "llama-meta-textgeneration"
)
