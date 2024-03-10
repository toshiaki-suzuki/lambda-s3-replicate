from .Replicater import Replicater
# from dotenv import load_dotenv

# import boto3
# import os
import re


class DifferentialReplicater(Replicater):
    def __init__(self, source_bucket, destination_bucket, source_prefixes, destination_prefix, s3_client):
        super().__init__(source_bucket=source_bucket,
                         destination_bucket=destination_bucket,
                         source_prefixes=source_prefixes,
                         destination_prefix=destination_prefix,
                         s3_client=s3_client)

    def execute(self):
        self.logger.info('Start DifferentialReplication')
        try:
            # 送信先バケットの既存ファイルを取得
            existing_file_set = self._getExistingFileSet()
            # 送信元フォルダをループ
            for prefix in self.source_prefixes:
                self._process_s3_objects(self.source_bucket,
                                         prefix,
                                         lambda item: self._replicate_difference(item, existing_file_set))
        except Exception as e:
            self.logger.error(e)
            return
        self.logger.info('Finish DifferentialReplication')

    def _getExistingFileSet(self):
        # 送信先バケットの既存ファイルを取得
        existing_file_set = set()
        # process_s3_objectと高階関数を使って、existing_file_setに値を追加
        self._process_s3_objects(self.destination_bucket,
                                 self.destination_prefix,
                                 lambda obj: existing_file_set.add(obj['Key']))
        return existing_file_set

    def _replicate_difference(self, item, existing_files):
        file_name = item['Key']
        # フォルダの場合はスキップ
        if file_name in self.source_prefixes:
            return
        destination_path = self._getDestinationPath(file_name)
        # 差分データのみコピー
        if destination_path not in existing_files:
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


# if __name__ == "__main__":
#     load_dotenv()
#     replicater = DifferentialReplicater(
#         source_bucket=os.environ['SOURCE_BUCKET'],
#         destination_bucket=os.environ['DESTINATION_BUCKET'],
#         source_prefixes=['source-folder1/', 'source-folder2/'],
#         destination_prefix='destination-folder/',
#         s3_client=boto3.client('s3')
#     )
#     replicater.execute()
