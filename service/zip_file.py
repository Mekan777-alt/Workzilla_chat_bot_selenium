import zipfile
import os


def zip_files(files_list):
    zip_filename = f'{os.getcwd()}/files/photos.zip'

    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for file in files_list:
            if os.path.exists(file):
                zipf.write(file)
            else:
                raise FileNotFoundError(file)
    return zip_filename

