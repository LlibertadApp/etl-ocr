import boto3
import os
import json

class MissingParameters(Exception):
  pass

def handler (input, context):

  # myEnvVarEjemplo = os.getenv('UNA_VAR_DE_ENTORNO')

  print('input:\n',input)

  # No se usa para nada cadaMesaId, es un ejemplo nomás.
  cadaMesaId = input['CADA_MESA_ID']

  missingInputsList = []
  if ('cadaMesaId' not in locals()) or (cadaMesaId == ""):
    missingInputsList.append("CADA_MESA_ID")

  if (missingInputsList):
    raise MissingParameters("Missing required input: " + ", ".join(missingInputsList) )

  s3 = boto3.client('s3')

  response = s3.list_buckets()
  buckets = response['Buckets']

  print("List of buckets:", buckets)
  return json.dumps(buckets, default=str)

