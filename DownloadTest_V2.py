from __future__ import print_function
import pickle
import os.path
import io
import shutil
import requests
from mimetypes import MimeTypes
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from pydrive.auth import GoogleAuth;from pydrive.drive import GoogleDrive
import dropbox;from dropbox.files import FolderMetadata

gauth = GoogleAuth();gauth.LocalWebserverAuth();drive = GoogleDrive(gauth)
DriveContents = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList() #for specific folder, replace root with folderID
access_token = 'HRIscS4SThMAAAAAAAAAAdMf56_ng1oQb2v_RDqO7Uj0jU623N_0j4xveTZIuCNU';dbx = dropbox.Dropbox(access_token)
DeepLabCut_Project_Folder = 'FMOS_Test'

for directory in DriveContents: #This chuck gets directory ID's for deeplabcut project, videos, and plot-poses folder
    if (directory['title'] == DeepLabCut_Project_Folder):
        ProjectID = directory['id']
        ProjectContents = drive.ListFile({'q': "'{}' in parents and trashed=false".format(ProjectID)}).GetList()
        for subDirectory in ProjectContents:
            if subDirectory['title'] == 'videos':
                VideoFolderID = subDirectory['id']
                Project_VideoContents = drive.ListFile({'q': "'{}' in parents and trashed=false".format(VideoFolderID)}).GetList()
                for content in Project_VideoContents:
                    if content['title']== 'plot-poses':
                        PlotPosesID = content['id']

File_ID_Destination = [];Local_OutputDirectory = 'testt/'
PlotPosesContent = drive.ListFile({'q': "'{}' in parents and trashed=false".format(PlotPosesID)}).GetList()
for item in PlotPosesContent:
    if item['title'].endswith('Trim'):
        childDir = Local_OutputDirectory + item['title']
        os.mkdir(childDir)
        ChildDirID = item['id']
        help = drive.ListFile({'q': "'{}' in parents and trashed=false".format(ChildDirID)}).GetList()
        for child in help:
            itemID = child['id']
            destination = childDir + '/' + child['title']
            File_ID_Destination.append(itemID+':'+destination)
for item in Project_VideoContents:
    if not item['title'].endswith('plot-poses'):
        itemNameSplit = item['title'].split('DLC')
        destination = Local_OutputDirectory+itemNameSplit[0]+'/'+item['title']
        itemID = item['id']
        File_ID_Destination.append(itemID + ':' + destination)
        print(itemID + ':' + destination)

print(File_ID_Destination)

class DriveAPI:
    global SCOPES
    SCOPES = ['https://www.googleapis.com/auth/drive']
    def __init__(self):
        self.creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        if not self.creds or not self.creds.valid:

            # If token is expired, it will be refreshed,
            # else, we will request a new one.
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        # Connect to the API service
        self.service = build('drive', 'v3', credentials=self.creds)
        results = self.service.files().list(
            pageSize=100, fields="files(id, name)").execute()
        items = results.get('files', [])
        #print("Here's a list of files: \n")
        #print(*items, sep="\n", end="\n\n")


    def FileDownload(self, file_id, file_name):
        request = self.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request, chunksize=204800)
        done = False

        try:
            while not done:
                status, done = downloader.next_chunk()
            fh.seek(0)
            # Write the received data to the file
            with open(file_name, 'wb') as f:
                shutil.copyfileobj(fh, f)
            print("File Downloaded")
            # Return True if file Downloaded successfully
            return True
        except:
            # Return False if something went wrong
            print("Something went wrong.")
            return False
x = 0
if __name__ == "__main__":
    while x < len(File_ID_Destination):
        for file in File_ID_Destination:
            obj = DriveAPI()
            fileSplit = file.split(':')
            f_id = fileSplit[0]
            f_name = fileSplit[1]
            obj.FileDownload(f_id, f_name)
            x+=1

def uploadGeneratedFiles():
    filestoUpload = []
    for folder in os.listdir(Local_OutputDirectory):
        folderPath = Local_OutputDirectory + folder+'/'
        filesin_FolderPath = os.listdir(folderPath)
        for file in filesin_FolderPath:
            filePath = folderPath+file
            filestoUpload.append(filePath)
    print(filestoUpload)
    class TransferData:
        def __init__(self, access_token):
            self.access_token = access_token
        def upload_file(self, file_from, file_to):
            dbx = dropbox.Dropbox(self.access_token)
            with open(file_from, 'rb') as f:
                dbx.files_upload(f.read(), file_to)
    def main():
        transferData = TransferData(access_token)
        file_from = location
        file_to = '/'+location  # The full path to upload the file to, including the file name
        transferData.upload_file(file_from, file_to)
    x = 0;
    while x < len(filestoUpload):
        if __name__ == '__main__':
            location = filestoUpload[x]
            main()
            x += 1;

uploadGeneratedFiles()