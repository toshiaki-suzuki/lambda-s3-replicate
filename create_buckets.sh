#!/bin/bash

echo "Creating buckets..."
aws --endpoint-url=http://localstack:4566 s3api create-bucket --bucket source-bucket
aws --endpoint-url=http://localstack:4566 s3api create-bucket --bucket destination-bucket
echo "Created buckets!"