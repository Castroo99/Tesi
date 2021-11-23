from infercode.client.infercode_client import InferCodeClient
import os
import logging
logging.basicConfig(level=logging.INFO)

rootdir = "extracted_func"

# Change from -1 to 0 to enable GPU
os.environ['CUDA_VISIBLE_DEVICES'] = "0"
path = "extracted_func/2"
infercode = InferCodeClient(language="c")
infercode.init_from_config()

# vectors = infercode.encode(["for (i = 0; i < n; i++)", "struct book{ int num; char s[27]; }shu[1000];"])

for file in os.listdir(rootdir):
    with open(rootdir + "/" + file, "r", encoding="latin1") as a_file:
        content = a_file.read()
        vectors = infercode.encode([content])
        print(vectors)

