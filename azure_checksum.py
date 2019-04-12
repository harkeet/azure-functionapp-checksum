import logging

import azure.functions as func

import hashlib

import os

import re

from azure.storage.blob import BlockBlobService

# DIrectory for the both file
#dir_name = '/Users/hbajaj/Learning/Azure/checksum/INT_SCM_ItemExport_59848_20190326102241'

#original_md5 = '20842e53bf0bb64b74d985ffcf427cdd'


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    #csv_filename = req.params.get('csv_filename')
    #checksum_filename = req.params.get('checksum_filename')
    filepath = req.params.get('Path')
    if not filepath:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            filepath = req_body.get('Path')

    zipfilename = req.params.get('Name')
    if not zipfilename:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            zipfilename = req_body.get('Name')

    if filepath and zipfilename:

        matchObj = re.match(r'[^/]+(?=(?:\.[^.]+)?$)', zipfilename)
        csv_filename = matchObj.group() + ".csv"
        block_blob_service = BlockBlobService(
            account_name='edsaasdrsa01', account_key='bN1m3zivsxx+wDqho7qqpw6kmz2zSINLgche+7POs6+X3GqFuN+KK94hjVa4QLGvNeS1in3n/mY+oSA8mh7bvA==')
        CONTAINERNAME = 'sourceblob'
        #BLOBNAME= 'ROSS/INT_SCM_201/INT_SCM_ItemExport_60743_20190329082159.zip'

        cutblob = re.split("/sourceblob/", filepath, 1)
        BLOBNAME = cutblob[1]
        csv_path = BLOBNAME + csv_filename
        checksum_path = BLOBNAME + "checksum.txt"
        block_blob_service.get_blob_to_path(
            CONTAINERNAME, csv_path, 'local_csv_file.csv')
        block_blob_service.get_blob_to_path(
            CONTAINERNAME, checksum_path, 'local_checksum.txt')
        #original_md5_file = os.path.join(dir_name, checksum_filename)
        original_md5_file = 'local_checksum.txt'
        with open(original_md5_file, 'r') as file:
            original_md5 = file.read().replace('\n', '')

        file_name = 'local_csv_file.csv'
        md5_returned = hashlib.md5(open(file_name, 'rb').read()).hexdigest()

        if original_md5 == md5_returned:
                #return func.HttpResponse(f"MD5 Verified")
                response = func.HttpResponse()
                #response.write("MD5 Verified")
                #response = "MD5 Verified"
                response.headers['HeaderPath'] = filepath
                response.headers['HeaderFile'] = csv_filename
                return response


        else:
            return func.HttpResponse(
                "MD5 Check Failed",
            status_code=420
        )

    else:
        return func.HttpResponse(
            "Please pass a Path and Name on the query string or in the request body",
            status_code=400
        )
