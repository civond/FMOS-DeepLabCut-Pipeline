from pydrive.auth import GoogleAuth;from pydrive.drive import GoogleDrive
import dropbox;from dropbox.files import FolderMetadata
from zdrive import Downloader
import os;import csv;
#みんなのドリアン <3

#-----------------Note: you have to set up the OAuth and back end permissions on dropbox / google drive prior to running this script -----------
#Necessary Authentication = client_secrets.json for Drive, OAuth token for DropBox
DeepLabCut_Project_Folder = 'FMOS_Test'

gauth = GoogleAuth();gauth.LocalWebserverAuth();drive = GoogleDrive(gauth)
DriveContents = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList() #for specific folder, replace root with folderID
access_token = 'HRIscS4SThMAAAAAAAAAAdMf56_ng1oQb2v_RDqO7Uj0jU623N_0j4xveTZIuCNU';dbx = dropbox.Dropbox(access_token)
Local_output_directory = "generatedContent/";d = Downloader() #This step uses ZDrive, not GoogleAPI!
folder_id = '1aqE91owiYbhuBsRdDNjGFzvIqvgPDYam' #videos folder that we want to download after video processing

def uploadDropboxVideos():
    for entry in dbx.files_list_folder('/ToProcess', recursive=True).entries:
        if isinstance(entry, dropbox.files.FileMetadata):
            if entry.path_display.endswith('.avi') or entry.path_display.endswith('.mp4'):
                DropBox_PathSplit = entry.path_display.split('/')
                Local_filepath= 'DropBox_Downloads/' + DropBox_PathSplit[len(DropBox_PathSplit)-1]
                f = open(Local_filepath, "wb")
                metadata, res = dbx.files_download(path=entry.path_display)
                f.write(res.content)
    Downloadedfiles = os.listdir('DropBox_Downloads/')
    with open('DropboxLocalDownloads_List.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(Downloadedfiles)
    print('DropBox Files Downloaded! Uploading to Google Drive now~ \n')

    for directory in DriveContents:
        if (directory['title'] == DeepLabCut_Project_Folder): #Project folder for DeepLabCut
            ProjectID = directory['id'] #Directory ID is in the GoogleDrive link
            ProjectContents = drive.ListFile({'q': "'{}' in parents and trashed=false".format(ProjectID)}).GetList()  # for specific folder, replace root with folderID
            for subDirectory in ProjectContents:
                if subDirectory['title'] == 'videos':
                    VideoFolderID = subDirectory['id']
        for rawVideo in os.listdir('DropBox_Downloads/'):
            rawVideo_Path = 'DropBox_Downloads/'+rawVideo
            if rawVideo.endswith('.mp4'):
                upload = drive.CreateFile({"mimeType": "video/mp4", "parents": [{"kind": "drive#fileLink", "id": VideoFolderID}]})
                upload.SetContentFile(rawVideo_Path)
                upload.Upload()  # Upload the file.
                print('Created file %s with mimeType %s' % (upload['title'], upload['mimeType']))
                os.remove(rawVideo_Path)
    uploadedVideo_IDs = []
    videoDirectory_Contents = drive.ListFile({'q': "'1aqE91owiYbhuBsRdDNjGFzvIqvgPDYam' in parents and trashed=false"}).GetList() #make sure this is correct!
    for video in videoDirectory_Contents:
        videoID = video['id'] #Google Drive ID for uploaded videos
        uploadedVideo_IDs.append(videoID)
    print(uploadedVideo_IDs)

    #processVideos = input("\nNow process your videos using Colabs! Press enter to continue~ : ")
    print('\nProceeding to next step (post-processing)\n')
    for videoID in uploadedVideo_IDs:
        originalVideo = drive.CreateFile({'id': videoID})
        #originalVideo.Delete()  # Permanently delete the file.
    print('original videos deleted')

    poop = input("\nNdddddddnter to continue~ : ")
    #generated_Content = drive.ListFile({'q': "'1aqE91owiYbhuBsRdDNjGFzvIqvgPDYam' in parents and trashed=false"}).GetList()
    '''
    for file in generated_Content:
        generatedContentID = file['id']
        drive.files.get(generatedContentID)
    
    for f in generated_Content:
        # 3. Create & download by id.
        print('title: %s, id: %s' % (f['title'], f['id']))
        fname = f['title']
        print('downloading to {}'.format(fname))
        f_ = drive.CreateFile({'id': f['id']})
        f_.GetContentFile(fname)
        
    '''

    d.downloadFolder(folder_id, destinationFolder=Local_output_directory)

def uploadGeneratedFiles():
    filestoUpload = []
    for item in os.listdir('generatedContent/'):
        filePath = 'generatedContent/' + item
        if item.endswith('.mp4') or item.endswith('.pickle') or item.endswith('.h5'):
            filestoUpload.append(filePath)
        else:
            for graph in os.listdir(filePath):
                directoryPath = filePath+'/'+graph
                filestoUpload.append(directoryPath)
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
        file_to = '/test_dropbox/'+location  # The full path to upload the file to, including the file name
        transferData.upload_file(file_from, file_to)
    x = 0;
    while x < len(filestoUpload):
        if __name__ == '__main__':
            location = filestoUpload[x]
            main()
            x+=1;

uploadDropboxVideos()
uploadGeneratedFiles()