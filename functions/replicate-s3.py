import boto3
import re
import os

s3_client = boto3.client('s3')


def lambda_handler(event, context):
    source_bucket = os.environ['SOURCE_BUCKET']  # 送信元のS3バケット名
    destination_bucket = os.environ['DESTINATION_BUCKET']  # 送信先のS3バケット名
    source_prefixes = ['source-folder1/', 'source-folder2/']  # 送信元の複数のフォルダ
    destination_prefix = 'destination-folder/'  # 送信先の基本フォルダパス

    # 送信先バケットの既存ファイルを取得
    existing_files = set()
    resp = s3_client.list_objects_v2(
        Bucket=destination_bucket, Prefix=destination_prefix)
    if 'Contents' in resp:
        for obj in resp['Contents']:
            existing_files.add(obj['Key'])

    for prefix in source_prefixes:
        # 送信元S3バケットのファイル一覧を取得
        response = s3_client.list_objects_v2(
            Bucket=source_bucket, Prefix=prefix)
        if 'Contents' in response:
            for item in response['Contents']:
                file_name = item['Key']

                # ファイル名から年月を抽出（任意のプレフィックスを許容）
                match = re.search(r'(.+)_(\d{4})(\d{2})\d{2}\.csv', file_name)
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
