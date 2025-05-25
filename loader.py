import shutil

local_file1 = 'app/langchain_vector_store/index.faiss'
local_file2 = 'app/langchain_vector_store/index.pkl'
nfs_path1 = '/mnt/nfs/index.faiss'
nfs_path2 = '/mnt/nfs/index.pkl'

shutil.copy(local_file1, nfs_path1)
shutil.copy(local_file2, nfs_path2)
print(f"Загружено")

import os

mount_point = '/mnt/nfs'

if os.path.ismount(mount_point):
    print(f"{mount_point} смонтирован.")
else:
    print(f"{mount_point} не смонтирован.")
