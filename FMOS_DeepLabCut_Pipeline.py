from pydrive.auth import GoogleAuth;from pydrive.drive import GoogleDrive
import dropbox;from dropbox.files import FolderMetadata
import os;import shutil;import requests
import pandas as pd

#みんなのドリアン <3

#-----------------Note: you have to set up the OAuth and back end permissions on dropbox / google drive prior to running this script -----------
#Necessary Authentication = client_secrets.json for GDrive,credentials.json, OAuth token for DropBox
DeepLabCut_Project_Folder = 'FMOS_Test'
gauth = GoogleAuth();gauth.LocalWebserverAuth();drive = GoogleDrive(gauth)
DriveContents = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList() #for specific folder, replace root with folderID
access_token = os.environ.get('Smear_FMOS_DropBox_Token');dbx = dropbox.Dropbox(access_token)
df = pd.read_csv('Uploaded_Videos.csv')
Local_OutputDirectory = 'colab_uploads/' #Downloads from Deeplabcut

for directory in DriveContents: #This chuck gets directory ID's for colab_uploads project, videos, and plot-poses folder
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

def uploadDropboxVideos():
    downloaded_files_DropBox = []
    for entry in dbx.files_list_folder('/Avinash Matt/Dropbox-Test/To process', recursive=True).entries:
        if isinstance(entry, dropbox.files.FileMetadata):
            if entry.path_display.endswith('.avi') or entry.path_display.endswith('.mp4'):
                DropBox_PathSplit = entry.path_display.split('/')
                Local_filepath= DropBox_PathSplit[len(DropBox_PathSplit)-1]
                if Local_filepath not in df.values:
                    print('DropBox: Downloading ' + Local_filepath)
                    f = open(Local_filepath, "wb")
                    metadata, res = dbx.files_download(path=entry.path_display)
                    f.write(res.content)
                    downloaded_files_DropBox.append(Local_filepath)
                else:
                    print('DropBox: ' + Local_filepath + 'is already processed! Skipping.')
    local_df = pd.DataFrame(downloaded_files_DropBox)
    local_df.to_csv('Downloaded_Videos.csv', index=False, mode='w')
    print('DropBox Files Downloaded! Uploading to Google Drive now~ \n')
    local_uploaded_videos = []
    for rawVideo in os.listdir():
        if rawVideo.endswith('.mp4') or rawVideo.endswith('.avi'):
            upload = drive.CreateFile({"mimeType": "video/mp4", "parents": [{"kind": "drive#fileLink", "id": VideoFolderID}]})
            upload.SetContentFile(rawVideo)
            upload.Upload()  # Upload the file.
            print('Created file %s with mimeType %s' % (upload['title'], upload['mimeType']))
            local_uploaded_videos.append(rawVideo);os.remove(rawVideo)
    uploaded_video_ids = []
    video_directory_contents = drive.ListFile({'q': "'{}' in parents and trashed=false".format(VideoFolderID)}).GetList()
    for video in video_directory_contents:
        videoID = video['id'] #Google Drive ID for uploaded videos
        uploaded_video_ids.append(videoID)

    processVideos = input("\nNow process your videos using Colabs! Press enter to continue~ : ")
    print('Proceeding to next step (post-processing)\n')
    for videoID in uploaded_video_ids:
        originalVideo = drive.CreateFile({'id': videoID})
        #originalVideo.Delete()  # Permanently delete the file.
    print('Uploaded videos from Drive deleted. Downloading remaining files locally :)')

def Download_FromDeepLabCut():
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
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
        URL = "https://drive.google.com/drive/u/0/folders/1aqE91owiYbhuBsRdDNjGFzvIqvgPDYam"
        session = requests.Session()
        response = session.get(URL, params={'id': id}, stream=True)
        token = get_confirm_token(response)
        if token:
            params = {'id': id, 'confirm': token}
            response = session.get(URL, params=params, stream=True)
        save_response_content(response, destination)
    #Local_OutputDirectory = 'colab_uploads uploads/'
    for item in Project_VideoContents:
        if not item['title'].endswith('Trim'):
            if item['title'] == 'plot-poses':
                continue
            itemID = item['id']
            destination = Local_OutputDirectory + item['title']
            download_file_from_google_drive(itemID, destination)
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
                print(destination)
                download_file_from_google_drive(itemID, destination)

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
        file_to = '/Avinash Matt/DeepLabCut/'+location  # The full path to upload the file to, including the file name
        transferData.upload_file(file_from, file_to)
    x = 0;
    while x < len(filestoUpload):
        if __name__ == '__main__':
            location = filestoUpload[x]
            main()
            x += 1;

print('Preparing to remove content in colab_uploads (local)')
confirm = input('Type DELETE to continue: ')
if confirm == 'DELETE':
    for item in os.listdir(Local_OutputDirectory):
        shutil.rmtree(Local_OutputDirectory+item)

uploadDropboxVideos()
Download_FromDeepLabCut()
uploadGeneratedFiles()