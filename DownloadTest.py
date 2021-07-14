from zdrive import Downloader
import os
import requests
from pydrive.auth import GoogleAuth;from pydrive.drive import GoogleDrive

gauth = GoogleAuth();gauth.LocalWebserverAuth();drive = GoogleDrive(gauth)
DriveContents = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList() #for specific folder, replace root with folderID
DeepLabCut_Project_Folder = 'FMOS_Test'

def download_file_from_google_drive(id, destination):
    def get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value
        return None
    def save_response_content(response, destination):
        CHUNK_SIZE = 32768

        with open(destination, "wb") as f:
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
    URL = "https://docs.google.com/uc?export=download"
    session = requests.Session()
    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)
    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)
    save_response_content(response, destination)

for directory in DriveContents:
    if (directory['title'] == DeepLabCut_Project_Folder):  # Project folder for DeepLabCut
        ProjectID = directory['id']
        ProjectContents = drive.ListFile({'q': "'{}' in parents and trashed=false".format(ProjectID)}).GetList()
        for subDirectory in ProjectContents:
            if subDirectory['title'] == 'videos':
                VideoFolderID = subDirectory['id']
video_directory_contents = drive.ListFile({'q': "'{}' in parents and trashed=false".format(VideoFolderID)}).GetList()
for item in video_directory_contents:
    if item['title'].endswith('.h5') or item['title'].endswith('.mp4') or item['title'].endswith('.pickle') or item['title'].endswith('.avi'):
        itemID = item['id']
        destination = 'testt/' + item['title']
        download_file_from_google_drive(itemID, destination)
    else:
        childDir = 'testt/'+item['title']
        os.mkdir(childDir)
        ChildDirID = item['id']
        help = drive.ListFile({'q': "'{}' in parents and trashed=false".format(ChildDirID)}).GetList()
        print(help)
        for child in help:
            itemID = child['id']
            destination = childDir+'/'+child['title']
            download_file_from_google_drive(itemID, destination)

