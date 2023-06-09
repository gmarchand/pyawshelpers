# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
import sys
import errno
import os
from pypbar import ProgressBar
from boto.s3.connection import S3Connection, Location
from boto.exception import S3ResponseError, S3CreateError
from boto.s3.key import Key
import boto3


class AWSS3(object):
    __client = None
    __logger = None

    def __init__(self, s3_client:boto3.client, region, logger=None):
        """
        :type logger: logging.Logger
        :param logger: Logger object which will be used for logging.
        """


        self.__logger = logger
        self.__client = s3_client
        self.__region = region

    def s3_key_exist(self, bucket, key):
        """return True if exist, else None"""
        try:
            self.__client_object(Bucket=bucket, Key=key)
            return True
        except self.__client.ClientError as exc:
            if exc.response["Error"]["Code"] != "404":
                return False

    def create_bucket(self, bucket_name):
        """
        :type bucket_name: str
        :param bucket_name: Bucket name.

        :return: bucket_name
        """

        try:
            self.__client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': self.__region})
        except self.__client.exceptions.BucketAlreadyOwnedByYou:
            self.__logger.info("bucket already and owned by you")
        return bucket_name
    

    def upload_file_to_s3(self, file, s3_bucket, s3_key):
        """Upload file to Amazon S3 bucket"""
        
        # Check if object already exists on S3 and skip upload if it does
        try:
            self.__client.head_object(Bucket=s3_bucket, Key=s3_key)
            # Object found on S3, skip upload
            self.__logger.info("Path found on S3! Skipping %s...", s3_key)
        # Object was not found on S3, proceed to upload
        except self.__client.exceptions.ClientError:
            print("Uploading %s in %s", file, s3_key)
            self.__client.upload_file(file, s3_bucket, s3_key)


    def sync_dir_to_s3(self, source_dir, s3_bucket, s3_key):
        """Sync `source_dir` directory to Amazon S3 bucket"""
        self.__logger.info("Sync of %s to %s - %s", source_dir, s3_bucket, s3_key)
        for root, dirs, files in os.walk(source_dir):
            for filename in files:
                # construct the full local path
                local_path = os.path.join(root, filename)
                # construct the full S3 path
                relative_path = os.path.relpath(local_path, source_dir)
                s3_path = os.path.join(s3_key, relative_path)
                # Upload file to S3
                self.__client.upload_file_to_s3(local_path, s3_bucket, s3_path)

    # def download_s3_files(s3_client, s3_urls: list, dir):
#     """Download a list of Amazon S3 URLs to a directory"""
#     files = []
#     for s3_url in s3_urls:
#         parse = S3Url(s3_url)
#         s3_bucket = parse.bucket
#         s3_key = parse.key
#         path_file = dir + s3_key
#         path_dir = os.path.dirname(path_file)
#         os.makedirs(path_dir, exist_ok=True)
#         logging.info(
#             "Downloading S3 object from (bucket:%s - key:%s) to %s",
#             s3_bucket,
#             s3_key,
#             path_file,
#         )
#         s3_client.download_file(s3_bucket, s3_key, path_file)
#         files.append(path_file)
#     return files

    # def upload_file(self, bucket, str_key, path_file):
    #     """
    #     :type bucket: boto.s3.bucket.Bucket
    #     :param bucket: Bucket object.

    #     :type str_key: str
    #     :param str_key: AWS S3 Bucket key.

    #     :type path_file: str
    #     :param path_file: Path to a file.
    #     """

    #     self.__logger.info('Uploading "%s" to [%s]:%s' % (path_file, bucket.name, str_key))

    #     k = Key(bucket)
    #     k.key = str_key
    #     pb = ProgressBar(width=20, prefix='%s ' % str_key)
    #     size = k.set_contents_from_filename(path_file, cb=pb.update)
    #     pb.finish()

    # def upload_file1(self, bucket_name, key, file_path):
    #     """
    #     :type bucket_name: str
    #     :param bucket_name: Bucket name.

    #     :type key: str
    #     :param key: AWS S3 bucket key.

    #     :type file_path: str
    #     :param file_path: Path to a file.
    #     """

    #     bucket = self.get_bucket(bucket_name)
    #     return self.upload_file(bucket, key, file_path)

    # def upload_directory(self, bucket, dir_path, key_prefix='/'):
    #     """
    #     :type bucket: boto.s3.bucket.Bucket
    #     :param bucket: Bucket object.

    #     :type dir_path: str
    #     :param dir_path: Path to a directory for uploading.

    #     :type key_prefix: str
    #     :param key_prefix: S3 key prefix.
    #     """

    #     self.__logger.info('Uploading directory "%s" to [%s]:%s' % (dir_path, bucket.name, key_prefix))

    #     try:
    #         filelist = os.listdir(dir_path)
    #     except OSError:
    #         self.__logger.error("Can't read a directory \"%s\"!" % dir_path)
    #         sys.exit(1)

    #     for filename in filelist:
    #         k = Key(bucket)
    #         k.key = "%s/%s" % (os.path.basename(dir_path), filename)
    #         pb = ProgressBar(prefix='%s ' % k.key)
    #         size = k.set_contents_from_filename(os.path.join(dir_path, filename), cb=pb.update)




    # def upload_directory1(self, bucket_name, dir_path):
    #     """
    #     :type bucket_name: str
    #     :param bucket_name: Bucket name.

    #     :type dir_path: str
    #     :param dir_path: Path to a directory for uploading.
    #     """

    #     bucket = self.get_bucket(bucket_name)
    #     return self.upload_directory(bucket, dir_path)

    # def download_file(self, bucket, str_key, path_destination):
    #     """
    #     :type bucket: boto.s3.bucket.Bucket
    #     :param bucket: Bucket object.

    #     :type str_key: str
    #     :param str_key: AWS S3 Bucket key.

    #     :type path_destination: str
    #     :param path_destination: Destination directory for saving.
    #     """

    #     self.__logger.info('Downloading file "%s" from [%s] to "%s"' % (str_key, bucket.name, path_destination))

    #     try:
    #         os.makedirs(path_destination)
    #     except OSError as exception:
    #         if exception.errno != errno.EEXIST:
    #             self.__logger.error("Can't create a directory \"%s\"!" % path_destination)
    #             raise exception
    #     file_path = os.path.join(path_destination, str_key)
    #     k = Key(bucket)
    #     k.key = str_key
    #     pb = ProgressBar(prefix='%s ' % str_key)
    #     k.get_contents_to_filename(file_path, cb=pb.update)

    # def download_file1(self, bucket_name, str_key, path_destination):
    #     """
    #     :type bucket_name: str
    #     :param bucket_name: Bucket name.

    #     :type str_key: str
    #     :param str_key: AWS S3 Bucket key.

    #     :type path_destination: str
    #     :param path_destination: Destination directory for saving.
    #     """

    #     bucket = self.get_bucket(bucket_name)
    #     return self.download_file(bucket, str_key, path_destination)

    # def download_directory(self, bucket, key_prefix, path_destination):
    #     """
    #     :type bucket: boto.s3.bucket.Bucket
    #     :param bucket: Bucket object.

    #     :type key_prefix: str
    #     :param key_prefix: AWS S3 Bucket key prefix (this is like FS path, S3 is a key-value storage).

    #     :type path_destination: str
    #     :param path_destination: Destination directory for saving.
    #     """

    #     self.__logger.info('Downloading directory "%s" from [%s] to "%s"' % (key_prefix, bucket.name, path_destination))

    #     try:
    #         os.makedirs(path_destination)
    #     except OSError as exception:
    #         self.__logger.error("Can't create a directory \"%s\"!" % path_destination)
    #         if exception.errno != errno.EEXIST:
    #             raise exception

    #     keys = bucket.get_all_keys(prefix=key_prefix)
    #     for ind, key in enumerate(keys):
    #         path_file = os.path.join(path_destination, key.key)
    #         path_file_dir = os.path.dirname(path_file)
    #         if not os.path.exists(path_file_dir):
    #             os.makedirs(path_file_dir)
    #         pb = ProgressBar(prefix='...%s ' % key.key[-20:], postfix=' File %s of %s' % (ind, len(keys)))
    #         key.get_contents_to_filename(path_file, cb=pb.update)
    #         pb.finish()

    # def download_directory1(self, bucket_name, key_prefix, path_destination):
    #     """
    #     :type bucket_name: str
    #     :param bucket_name: Bucket name.

    #     :type key_prefix: str
    #     :param key_prefix: AWS S3 Bucket key prefix (this is like FS path, S3 is a key-value storage).

    #     :type path_destination: str
    #     :param path_destination: Destination directory for saving.
    #     """

    #     bucket = self.get_bucket(bucket_name)
    #     return self.download_directory(bucket, key_prefix, path_destination)
