import boto3
from abc import ABCMeta, abstractmethod


class Replicater(metaclass=ABCMeta):
    failded_files = []
    s3_client = boto3.client('s3')

    def __init__(self, target_buckets, source_prefixes, destination_prefix):
        self.target_buckets = target_buckets
        self.source_prefixes = source_prefixes
        self.destination_prefix = destination_prefix

    @abstractmethod
    def execute(self):
        pass
