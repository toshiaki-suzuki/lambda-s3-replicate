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

    # モック用のヘルパーメソッド
    def mock_s3_list_objects_v2(bucket, prefix, keys):
        return {'Contents': [{'Key': key} for key in keys]} if keys else {}

    # LocalStackのS3にデータを投入するヘルパーメソッド
    def put_s3_data(bucket, prefix, keys):
        for key in keys:
            s3_client.put_object(Bucket=bucket, Key=f'{prefix}{key}')

    @pytest.fixture(autouse=True)
    def setup(self):
        # テスト前に送信元バケットと送信先バケットを空にする
        s3_client.delete_object(Bucket=source_bucket,
                                Key='source-folder1/file1_20230101.csv')
        s3_client.delete_object(Bucket=source_bucket,
                                Key='source-folder2/file2_20230201.csv')
        s3_client.delete_object(Bucket=source_bucket,
                                Key='other-folder/file3_20230301.csv')
        s3_client.delete_object(Bucket=destination_bucket,
                                Key='destination-folder/2023/01/file1_20230101.csv')
        s3_client.delete_object(Bucket=destination_bucket,
                                Key='destination-folder/2023/01/file2_20230201.csv')
        s3_client.delete_object(Bucket=destination_bucket,
                                Key='destination-folder/2023/01/file3_20230301.csv')

        # テスト前に送信元バケットと送信先バケットにデータを投入する
        # s3_client.put_object(Bucket=source_bucket,
        #                      Key='source-folder1/',
        #                      Body='file1_20230101.csv')
        # s3_client.put_object(Bucket=source_bucket,
        #                      Key='source-folder2/',
        #                      Body='file2_20230201.csv')
        # s3_client.put_object(Bucket=source_bucket,
        #                      Key='other-folder/',
        #                      Body='file3_20230301.csv')
        # s3_client.put_object(Bucket=destination_bucket,
        #                      Key='destination-folder/2023/01/',
        #                      Body='file1_20230101.csv')
        # s3_client.put_object(Bucket=destination_bucket,
        #                      Key='destination-folder/2023/01/',
        #                      Body='file2_20230101.csv')
        # s3_client.put_object(Bucket=destination_bucket,
        #                      Key='destination-folder/2023/01/',
        #                      Body='file3_20230101.csv')

    def test_replication_from_source_to_destination(self):
        """
        送信元バケットから送信先バケットにオブジェクトの複製ができていることをテスト
        """

        s3_client = boto3.client(
            's3',
            region_name='us-east-1',  # LocalStackではリージョンは任意ですが、指定する必要があります
            endpoint_url=localstack_url
        )
        s3_client.put_object(Bucket=source_bucket,
                             Key='source-folder1/file1_20230101.csv',
                             Body='file1_20230101.csv')

        # Lambda関数の実行
        lambda_handler(None, None)

        # テスト検証
        response = s3_client.list_objects_v2(
            Bucket=destination_bucket,
            Prefix='destination-folder/')
        expected = 'destination-folder/2023/01/file1_20230101.csv'
        actual = response['Contents'][0]['Key']
        assert expected == actual
