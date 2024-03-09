from Replicater import Replicater


class DifferentialReplicater(Replicater):
    def __init__(self, target_buckets, source_prefixes, destination_prefix):
        super().__init__(target_buckets, source_prefixes, destination_prefix)

    def execute(self):
        print("DifferentialReplicater execute method")


if __name__ == "__main__":
    replicater = DifferentialReplicater(
        target_buckets=[],
        source_prefixes=[],
        destination_prefix="hoge"
    )
    replicater.execute()
