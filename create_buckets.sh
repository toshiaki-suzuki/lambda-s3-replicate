#!/bin/bash

echo "Creating buckets..."
aws --endpoint-url=http://localstack:4566 s3api create-bucket --bucket 送信元バケット名 # 送信元バケット名を書き換える
aws --endpoint-url=http://localstack:4566 s3api create-bucket --bucket 送信先バケット名 # 送信先バケット名を書き換える
echo "Created buckets!"