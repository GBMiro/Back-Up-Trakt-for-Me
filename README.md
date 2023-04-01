# Back Up Trakt for Me

Python application that makes a backup of your Trakt.tv data: history, collection, lists (including watchlist), ratings, and watched (more coming later).

You can also check your history in a table and filter it by media type and/or year.

![BackupTraktForMe](https://user-images.githubusercontent.com/15947095/229277722-2cb28355-0bcd-424c-9692-7abf27f5e1e2.png)



# Setup

## Code and requirements

* Download the source code or clone the repo
* Install the requirements

  ``pip install -r requirements.txt``

## Trakt API

* Create a new application in [Trakt](https://trakt.tv/oauth/applications/new). Fill the required fields:
  * Name
  * Description
  * Redirect uri (use the one for device authentication that you find below the field)
* Save APP. You will be given a new Client ID and Client Secret for your app.

# How to use

## Interactive mode
  
``python BackupTraktForMe.py``
  
### Configuration

> NOTE: All settings are automatically stored in the database

* Go to the settings tab and copy/paste the Client ID and Client Secret you got creating your Trakt application into their respective fields.
* Click *Authorize User*

![Settings](https://user-images.githubusercontent.com/15947095/229280954-483bec76-7008-4237-b79f-7d63c91ad6ff.png)


* If your client ID and Secret are correct, the console will give you a code that you must enter in the Trakt [website](https://trakt.tv/activate) and give permission to the application.

![ReceivedCode](https://user-images.githubusercontent.com/15947095/229281228-6af41148-ce48-4758-be85-3fb73ae572b3.PNG)

* Once authorized, the access and refresh tokens will appear and you can start backing up your data.

  > NOTE: The access token expires in 3 months. If you get an error saying so when backing up your data, click *Refresh Tokens* and try again. If this does not work, click *Delete Tokens* and authorize the user again.
* You can select the folder where the backups will be stored. By default, this location is the same as the application folder.


### Backing up your data

* Go to Backup and click *Back Up Trakt*
* The application will export all your data in json format in a new folder created in your backup path. It will also store your trakt history (movies & episodes) in the database so you can check it in the table.
* The console will show messages of the tasks the application performs. If any export does not finish successfully it will show so with a red message. If the export is a success, it will show so with a green message.

![Backup](https://user-images.githubusercontent.com/15947095/229284501-9b366635-6ff2-4f0c-8807-b7adcbf196d1.gif)


### Checking your history

The *Backup* tab also shows a table with your Trakt history and you can filter this table by media and year. The table will automatically update itself after a backup or a filter change.
More features like this are planned for the future.

![Filters](https://user-images.githubusercontent.com/15947095/229284495-887402d2-e2c3-4d71-ae39-7c6abd96af69.gif)

## Non-interactive mode

> Before using non-interactive mode, you must run the application with interactive mode to set your Trakt configuration

You can create an automatic task to back up Trakt daily with no interaction needed. How you create this task depends on your OS.

``python BackupTraktForMe.py --no_user_interface``





