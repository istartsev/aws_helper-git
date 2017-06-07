import boto3


class BaseAWS3Helper(object):
    def __init__(self, service_name, region, access_key, secret_key):
        self._client = boto3.client(service_name=service_name,
                                    region_name=region,
                                    aws_access_key_id=access_key,
                                    aws_secret_access_key=secret_key)
