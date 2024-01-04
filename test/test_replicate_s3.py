import boto3
import pytest
import os
from functions.replicate_s3 import lambda_handler

localstack_url = 'http://localhost:4566'

# S3クライアントの設定
s3_client = boto3.client(
    's3',
    region_name='us-east-1',  # LocalStackではリージョンは任意ですが、指定する必要があります
    endpoint_url=localstack_url,
    aws_access_key_id='test',  # LocalStackでは任意の値でOK
    aws_secret_access_key='test'  # LocalStackでは任意の値でOK
)

source_bucket = os.environ['SOURCE_BUCKET']  # 送信元のS3バケット名
destination_bucket = os.environ['DESTINATION_BUCKET']  # 送信先のS3バケット名


class TestLambdaHandler:

    @pytest.fixture(autouse=True)
    def setup(self):
        # テスト前に送信元バケットと送信先バケットを空にする

        # 送信元バケット内のすべてのオブジェクトを取得
        source_bucket_object_list = s3_client.list_objects_v2(
            Bucket=source_bucket)
        if 'Contents' in source_bucket_object_list:
            for obj in source_bucket_object_list['Contents']:
                print(obj['Key'])
                s3_client.delete_object(
                    Bucket=source_bucket, Key=obj['Key'])

        # 送信先バケット内のすべてのオブジェクトを取得
        destination_bucket_object_list = s3_client.list_objects_v2(
            Bucket=destination_bucket)
        if 'Contents' in destination_bucket_object_list:
            for obj in destination_bucket_object_list['Contents']:
                print(obj['Key'])
                s3_client.delete_object(
                    Bucket=destination_bucket, Key=obj['Key'])

    def test_replication_from_source_to_destination(self):
        """
        送信元バケットから送信先バケットにオブジェクトの複製ができていることをテスト
        """

        # source-folder1にコピー対象データを投入
        s3_client.put_object(Bucket=source_bucket,
                             Key='source-folder1/file1_20230101.csv',
                             Body='file1_20230101.csv')
        # source-folder2にコピー対象データを投入
        s3_client.put_object(Bucket=source_bucket,
                             Key='source-folder2/file2_20240201.csv',
                             Body='file1_20240201.csv')
        # source-folder2に既存データを投入
        s3_client.put_object(Bucket=source_bucket,
                             Key='source-folder2/file1_20230101.csv',
                             Body='file1_20230101.csv')
        # other-folderにコピー対象外データを投入
        s3_client.put_object(Bucket=source_bucket,
                             Key='other-folder/file3_20230301.csv',
                             Body='file1_20230301.csv')

        # Lambda関数の実行
        lambda_handler(None, None)

        # テスト検証
        response = s3_client.list_objects_v2(
            Bucket=destination_bucket,
            Prefix='destination-folder/')

        # source-folder1からの複製ができていること
        # ファイル名のYYYY/MMがプレフィックスになっていること
        expected1 = 'destination-folder/2023/01/file1_20230101.csv'
        actual1 = response['Contents'][0]['Key']
        assert expected1 == actual1

        # source-folder2からの複製ができていることを検証
        # ファイル名のYYYY/MMがプレフィックスになっていること
        expected2 = 'destination-folder/2024/02/file2_20240201.csv'
        actual2 = response['Contents'][1]['Key']
        assert expected2 == actual2

        # destination-bucketに入っているオブジェクト数が2件であることを検証し下記を検証
        # 対象外のフォルダのファイルをコピーしていないこと
        # file1_20230101.csvが1件だけであること
        expected3 = 2
        actual3 = len(response['Contents'])
        assert expected3 == actual3
