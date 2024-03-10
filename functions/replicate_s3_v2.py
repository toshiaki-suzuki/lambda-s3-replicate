import boto3
import os

from dotenv import load_dotenv

from .DifferentialReplicater import DifferentialReplicater

load_dotenv()

source_bucket = os.environ['SOURCE_BUCKET']  # 送信元のS3バケット名
destination_bucket = os.environ['DESTINATION_BUCKET']  # 送信先のS3バケット名
source_prefixes = ['source-folder1/', 'source-folder2/']  # 送信元の複数のフォルダ
destination_prefix = 'destination-folder/'  # 送信先の基本フォルダパス
s3_client = boto3.client('s3')


def lambda_handler(event, context):
    replicater = DifferentialReplicater(
        source_bucket=source_bucket,
        destination_bucket=destination_bucket,
        source_prefixes=source_prefixes,
        destination_prefix=destination_prefix,
        s3_client=s3_client,
    )
    replicater.execute()
