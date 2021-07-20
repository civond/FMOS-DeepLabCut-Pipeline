import dropbox;from dropbox.files import FolderMetadata

access_token = 'nDHSmNK9uAwAAAAAAAAAAZNX0AET4dP2vt2Gghkvq1rF6NhM4wM3F8NqjBnacZgh'
dbx = dropbox.Dropbox(access_token)

for entry in dbx.files_list_folder('/Avinash Matt/Dropbox-Test', recursive=True).entries:
    if isinstance(entry, dropbox.files.FileMetadata):
        if entry.path_display.endswith('.h5') or entry.path_display.endswith('.mp4'):
            DropBox_PathSplit = entry.path_display.split('/')
            Local_filepath = DropBox_PathSplit[len(DropBox_PathSplit) - 1]
            f = open(Local_filepath, "wb")
            metadata, res = dbx.files_download(path=entry.path_display)
            f.write(res.content)
print('DropBox Files Downloaded! Uploading to Google Drive now~ \n')