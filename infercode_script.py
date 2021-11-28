from infercode.client.infercode_client import InferCodeClient
import os
import logging
import tensorflow as tf

# Change from -1 to 0 to enable GPU
os.environ['CUDA_VISIBLE_DEVICES'] = "0"

logging.basicConfig(level=logging.INFO)
rootdir = "extracted_func"
path = "extracted_func/MDEwOlJlcG9zaXRvcnk0MDc0MzcxNg==-source-Wi-FiTestSuite-Wi-FiTestSuite-Linux-DUT-f7a8d7e-lib-wfa_thr.c-wfa_wmm_thread.txt"

# MDEwOlJlcG9zaXRvcnk0MDc0MzcxNg==-source-Wi-FiTestSuite-Wi-FiTestSuite-Linux-DUT-f7a8d7e-lib-wfa_thr.c-wfa_wmm_thread.txt
# MDEwOlJlcG9zaXRvcnk0MDc0MzcxNg==-source-Wi-FiTestSuite-Wi-FiTestSuite-Linux-DUT-f7a8d7e-lib-wfa_cmdproc.c-xcCmdProcStaPresetTestParameters.txt

infercode = InferCodeClient(language="c")
infercode.init_from_config()
'''with open(path, "r", encoding="latin1") as a_file:
    content = str(a_file.read())
vectors = infercode.encode([content])
print(vectors)'''

big_trees = [
    "MDEwOlJlcG9zaXRvcnk0MDc0MzcxNg==-source-Wi-FiTestSuite-Wi-FiTestSuite-Linux-DUT-f7a8d7e-lib-wfa_thr.c-wfa_wmm_thread.txt",
    "MDEwOlJlcG9zaXRvcnk0MDg1Nzk3-source-gfto-oscam-2780c48-module-webif.c-send_oscam_reader_config.txt",
    "MDEwOlJlcG9zaXRvcnk0MDg1Nzk3-source-gfto-oscam-2780c48-oscam-ecm.c-get_cw.txt",
    "MDEwOlJlcG9zaXRvcnk0MDg1Nzk3-source-gfto-oscam-2780c48-reader-viaccess.c-CommonMain_D2_13_15.txt",
    "MDEwOlJlcG9zaXRvcnk0MDg1Nzk3-source-gfto-oscam-2780c48-reader-viaccess.c-hdSurEncCryptLookup_D2_0F_11.txt",
    "MDEwOlJlcG9zaXRvcnk0MDM5NTEyNg==-source-lfittl-libpg_query-0f8ad86-src-postgres-src_backend_nodes_copyfuncs.c-copyObjectImpl.txt",
    "MDEwOlJlcG9zaXRvcnk0MDM5NTEyNg==-source-lfittl-libpg_query-0f8ad86-src-postgres-src_backend_nodes_equalfuncs.c-equal.txt",
    "MDEwOlJlcG9zaXRvcnk0MDM5NTEyNg==-source-lfittl-libpg_query-0f8ad86-src-postgres-src_backend_parser_gram.c-base_yyparse.txt",
    "MDEwOlJlcG9zaXRvcnk0MDM5NTEyNg==-source-lfittl-libpg_query-0f8ad86-src-postgres-src_backend_parser_scan.c-core_yylex.txt"]

os.makedirs("extracted_vector", 0o777, True)

for subdir, dirs, files in os.walk(rootdir):
    for file in files:
        with open(os.path.join(subdir, file), "r", encoding="latin1") as a_file:
            content = str(a_file.read())
        print(file)
        print(os.path.getsize(os.path.join(subdir, file)))
        if not file in big_trees:
            try:
                vectors = infercode.encode([content])
                vectors_dataset = open(
                    os.path.join("extracted_vector", file + ".txt"),
                    "w", encoding="latin1")
                vectors_dataset.write(str(vectors))
                vectors_dataset.close()
                print(vectors)
            except:
                big_trees.append(file)
                continue
