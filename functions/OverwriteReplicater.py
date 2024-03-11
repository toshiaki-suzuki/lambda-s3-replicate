from Replicater import Replicater
from dotenv import load_dotenv

import boto3
import os
import re


class OverwriteReplicater(Replicater):
    def __init__(self, source_bucket, destination_bucket, source_prefixes, destination_prefix, s3_client):
        super().__init__(source_bucket=source_bucket,
                         destination_bucket=destination_bucket,
                         source_prefixes=source_prefixes,
                         destination_prefix=destination_prefix,
                         s3_client=s3_client)

    def execute(self):
        self.logger.info('Start OverwriteReplication')
        try:
            # 送信元フォルダをループ
            for prefix in self.source_prefixes:
                self._process_s3_objects(self.source_bucket,
                                         prefix,
                                         lambda item: self._replicate_or_overwrite(item))
        except Exception as e:
            self.logger.error(e)
            return
        self.logger.info('Finish OverwriteReplication')

    def _replicate_or_overwrite(self, item):
        file_name = item['Key']
        # フォルダの場合はスキップ
        if file_name in self.source_prefixes:
            return
        destination_path = self._getDestinationPath(file_name)
        # 差分データのみコピー
        self.s3_client.copy_object(Bucket=self.destination_bucket,
                                   CopySource={
                                       'Bucket': self.source_bucket,
                                       'Key': file_name},
                                   Key=destination_path)

    def _getDestinationPath(self, file_name):
        # ファイル名から年月を抽出（任意のプレフィックスを許容）
        pattern = r'(.+)_(\d{4})(\d{2})\d{2}\.csv'
        match = re.search(pattern, file_name)
        if not match:
            return
        _, year, month = match.groups()
        # 送信先のパスを設定
        destination_path = f'{self.destination_prefix}{year}/{month}/{file_name.split("/")[-1]}'
        return destination_path


if __name__ == "__main__":
    load_dotenv()
    replicater = OverwriteReplicater(
        source_bucket=os.environ['SOURCE_BUCKET'],
        destination_bucket=os.environ['DESTINATION_BUCKET'],
        source_prefixes=['source-folder1/', 'source-folder2/'],
        destination_prefix='destination-folder/',
        s3_client=boto3.client('s3')
    )
    replicater.execute()
