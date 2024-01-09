import boto3
import re
import os
from dotenv import load_dotenv

load_dotenv()


def lambda_handler(event, context):
    s3_client = boto3.client('s3')
    if os.environ['STAGE'] == 'test':
        # LocalStackのホストとポートを指定
        localstack_url = 'http://localhost:4566'

        # S3クライアントの設定
        s3_client = boto3.client(
            's3',
            region_name='ap-northeast-1',  # LocalStackではリージョンは任意ですが、指定する必要があります
            endpoint_url=localstack_url,
            aws_access_key_id='test',  # LocalStackでは任意の値でOK
            aws_secret_access_key='test'  # LocalStackでは任意の値でOK
        )

    source_bucket = os.environ['SOURCE_BUCKET']  # 送信元のS3バケット名
    destination_bucket = os.environ['DESTINATION_BUCKET']  # 送信先のS3バケット名
    source_prefixes = ['source-folder1/', 'source-folder2/']  # 送信元の複数のフォルダ
    destination_prefix = 'destination-folder/'  # 送信先の基本フォルダパス

    # 送信先バケットの既存ファイルを取得
    existing_files = set()
    pagenator = s3_client.get_paginator('list_objects_v2')

    # ページネーションで全件取得
    for page in pagenator.paginate(Bucket=destination_bucket, Prefix=destination_prefix):
        if 'Contents' in page:
            for obj in page['Contents']:
                existing_files.add(obj['Key'])

    # 送信元フォルダをループ
    for prefix in source_prefixes:
        # 送信元フォルダのファイル一覧を取得
        for page in pagenator.paginate(Bucket=source_bucket, Prefix=prefix):
            if 'Contents' in page:
                for item in page['Contents']:
                    file_name = item['Key']

                    # フォルダの場合はスキップ
                    if file_name == prefix:
                        continue

                    # ファイル名から年月を抽出（任意のプレフィックスを許容）
                    match = re.search(
                        r'(.+)_(\d{4})(\d{2})\d{2}\.csv', file_name)
                    if match:
                        _, year, month = match.groups()
                        # 送信先のパスを設定
                        destination_path = f'{destination_prefix}{year}/{month}/{file_name.split("/")[-1]}'

                        # 差分データのみコピー
                        if destination_path not in existing_files:
                            s3_client.copy_object(Bucket=destination_bucket,
                                                  CopySource={
                                                      'Bucket': source_bucket, 'Key': file_name},
                                                  Key=destination_path)

    return {
        'statusCode': 200,
        'body': 'File transfer completed for new files.'
    }
