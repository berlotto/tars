import gzip
from io import BytesIO

# Thanks Alfe for this code!
# https://stackoverflow.com/questions/15525837/which-is-the-best-way-to-compress-json-to-store-in-a-memory-based-store-like-red

def decompressBytesToString(inputBytes):
  """
  decompress the given byte array (which must be valid 
  compressed gzip data) and return the decoded text (utf-8).
  """
  bio = BytesIO()
  stream = BytesIO(inputBytes)
  decompressor = gzip.GzipFile(fileobj=stream, mode='r')
  while True:  # until EOF
    chunk = decompressor.read(8192)
    if not chunk:
      decompressor.close()
      bio.seek(0)
      return bio.read().decode("utf-8")
    bio.write(chunk)
  return None

def compressStringToBytes(inputString):
  """
  read the given string, encode it in utf-8,
  compress the data and return it as a byte array.
  """
  bio = BytesIO()
  bio.write(inputString.encode("utf-8"))
  bio.seek(0)
  stream = BytesIO()
  compressor = gzip.GzipFile(fileobj=stream, mode='w')
  while True:  # until EOF
    chunk = bio.read(8192)
    if not chunk:  # EOF?
      compressor.close()
      return stream.getvalue()
    compressor.write(chunk)