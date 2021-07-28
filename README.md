<h1>FMOS-DeepLabCut-Pipeline</h1>
<br/> Using Dropbox's and Google Drive's API in Python, this script streamlines the tedious process of managing files across shared workspaces for use in DeepLabCut's Google Colabs notebook. For added security, workplace OAuth tokens are hidden within local environmental variables.

<br/><h2>Usage</h2>
Assuming that you have the back end permissions for Dropbox and Google Drive set up properly (OAuth tokens, client_secrets.json, ect.), simply drop videos that need to be processed into "toProcess" in our shared Dropbox, and the script will do the rest. 
<br/>(Note, that you will have to authenticate for Google Drive and run the Colabs notebook on your own. This script only moves relevant files to the correct locations).

