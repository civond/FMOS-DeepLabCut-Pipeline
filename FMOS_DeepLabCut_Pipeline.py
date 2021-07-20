from pydrive.auth import GoogleAuth;from pydrive.drive import GoogleDrive
import dropbox;from dropbox.files import FolderMetadata
import os;import csv;import requests
#みんなのドリアン <3

#-----------------Note: you have to set up the OAuth and back end permissions on dropbox / google drive prior to running this script -----------
#Necessary Authentication = client_secrets.json for GDrive,credentials.json, OAuth token for DropBox
DeepLabCut_Project_Folder = 'FMOS_Test'

gauth = GoogleAuth();gauth.LocalWebserverAuth();drive = GoogleDrive(gauth)
DriveContents = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList() #for specific folder, replace root with folderID
access_token = 'HRIscS4SThMAAAAAAAAAAdMf56_ng1oQb2v_RDqO7Uj0jU623N_0j4xveTZIuCNU';dbx = dropbox.Dropbox(access_token)

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

def uploadDropboxVideos():
    for entry in dbx.files_list_folder('/ToProcess', recursive=True).entries:
        if isinstance(entry, dropbox.files.FileMetadata):
            if entry.path_display.endswith('.avi') or entry.path_display.endswith('.mp4'):
                DropBox_PathSplit = entry.path_display.split('/')
                Local_filepath= DropBox_PathSplit[len(DropBox_PathSplit)-1]
                f = open(Local_filepath, "wb")
                metadata, res = dbx.files_download(path=entry.path_display)
                f.write(res.content)
    print('DropBox Files Downloaded! Uploading to Google Drive now~ \n')
    for rawVideo in os.listdir():
        if rawVideo.endswith('.mp4') or rawVideo.endswith('.avi'):
            upload = drive.CreateFile({"mimeType": "video/mp4", "parents": [{"kind": "drive#fileLink", "id": VideoFolderID}]})
            upload.SetContentFile(rawVideo)
            upload.Upload()  # Upload the file.
            print('Created file %s with mimeType %s' % (upload['title'], upload['mimeType'])) ################################
            os.remove(rawVideo)
    uploaded_video_ids = []
    video_directory_contents = drive.ListFile({'q': "'{}' in parents and trashed=false".format(VideoFolderID)}).GetList()

    for video in video_directory_contents:
        videoID = video['id'] #Google Drive ID for uploaded videos
        uploaded_video_ids.append(videoID)

    #processVideos = input("\nNow process your videos using Colabs! Press enter to continue~ : ")
    print('\nProceeding to next step (post-processing)\n')
    for videoID in uploaded_video_ids:
        originalVideo = drive.CreateFile({'id': videoID})
        #originalVideo.Delete()  # Permanently delete the file.
    print('Uploaded videos from Drive deleted. Downloading remaining files locally :)')
    #Drive_Video_Folder = VideoFolderID  # videos folder that we want to download after video processing

def Upload_FromDeepLabCut():
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
    Local_OutputDirectory = 'testt/'
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
#uploadDropboxVideos()
Upload_FromDeepLabCut()
#uploadGeneratedFiles()