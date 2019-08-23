"""Minio Stuff
"""

class MinioCreds:
    def __init__(self, host: str, key: str, password: str):
        self.key = key
        self.password = password
        self.host = host


class MinioPath:
    def __init__(self, bucket:str, filename:str=''):
        self.bucket = bucket
        self.filename = filename