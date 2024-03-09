from abc import ABCMeta, abstractmethod
import logging


class Replicater(metaclass=ABCMeta):
    failded_files = []

    def __init__(self, source_bucket, destination_bucket, source_prefixes, destination_prefix, s3_client):
        self.source_bucket = source_bucket
        self.destination_bucket = destination_bucket
        self.source_prefixes = source_prefixes
        self.destination_prefix = destination_prefix
        self.s3_client = s3_client
        self.logger = logging.getLogger(__name__)

        self.logger.setLevel(logging.INFO)

    @abstractmethod
    def execute(self):
        pass

    # ページネーションを使って全件を高階関数で処理
    def _process_s3_objects(self, bucket, prefix, callback):
        paginator = self.s3_client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            if not ('Contents' in page):
                continue
            for obj in page['Contents']:
                callback(obj)
