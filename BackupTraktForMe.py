from AppController import AppController
from Utils.Logger import Logger
import Utils.StatusCodes as StatusCodes
import Utils.UI as UI
import Utils.Database as DB
import dearpygui.dearpygui as GUI
import argparse

# Trakt configuration functions

def AuthorizeUser(sender, app_data, user_data):
    id = GUI.get_value(UI.CLIENT_ID)
    secret = GUI.get_value(UI.CLIENT_SECRET)
    controller.SetTraktConfig(id, secret)
    controller.AuthorizeTraktUser()
    UpdateUISettings()

def RefreshUserToken(sender, app_data, user_data):
    controller.RefreshTraktToken()
    UpdateUISettings()

# Application functions

def BackupTrakt():
    controller.BackupTrakt()
    UpdateHistoryTable()

def SelectBackupFolder(app_data):
    logger.ShowMessage(app_data)
    controller.SetBackupFolder(app_data['file_path_name'])
    UpdateUISettings()

def SelectBackupFolderCancelled():
    logger.ShowMessage("Folder was not changed")

def ClearConsole():
    logger.Clear()

def ScrollDown():
    logger.ScrollToBottom()

def UpdateUIYearsCombo():
    yearsDB, statusCode = controller.GetHistoryYears()
    comboYears = ["All"]
    if (statusCode == StatusCodes.CONTROLLER_OK):
        for year in yearsDB:
            comboYears.append(year['year'])    
    GUI.configure_item(UI.YEAR_COMBO, items=comboYears)
    GUI.configure_item(UI.YEAR_COMBO, default_value=comboYears[0])
    GUI.set_value

def UpdateUISettings():
    GUI.set_value(UI.CLIENT_ID, controller.GetClientID())
    GUI.set_value(UI.CLIENT_SECRET, controller.GetClientSecret())
    GUI.set_value(UI.ACCES_TOKEN, controller.GetAccessToken())
    GUI.set_value(UI.REFRESH_TOKEN, controller.GetRefreshToken())
    GUI.set_value(UI.BACKUP_FOLDER, controller.GetBackupFolder())


def UpdateHistoryTable():
    GUI.delete_item(UI.HISTORY_TABLE, children_only=True)
    media = GUI.get_value(UI.TYPE_COMBO)
    year = GUI.get_value(UI.YEAR_COMBO)
    movies = True if (media == "All" or media == "Movies") else False
    episodes = True if (media =="All" or media == "Episodes") else False
    AddColumnsToTable(movies, episodes)
    if (year == "All"):
        year = ""
    data, statusCode = controller.GetHistoryData(movies, episodes, year)

    if (statusCode == StatusCodes.CONTROLLER_OK):
        for play in data:
            type = play[DB.TYPE_COLUMN]
            id = play[DB.ID_COLUMN]
            season = "-" if type == 'movie' else play[DB.SEASON_COLUMN]
            episodeNumber = "-" if type == 'movie' else play[DB.NUMBER_COLUMN]
            episodeTitle = "-" if type == 'movie' else play[DB.EPISODE_TITLE_COLUMN]
            name = play[DB.TITLE_COLUMN]
            date = play[DB.DATE_COLUMN]
            
            with GUI.table_row(parent=UI.HISTORY_TABLE):
                GUI.add_text(id)
                GUI.add_text(date)
                GUI.add_text(name)
                GUI.add_text(season)
                GUI.add_text(episodeNumber)
                GUI.add_text(episodeTitle)
                
        logger.ShowMessage("Showing {} plays from last database backup".format(len(data)))


def AddColumnsToTable(movies, episodes):

    GUI.add_table_column(parent=UI.HISTORY_TABLE, label="Play ID")
    GUI.add_table_column(parent=UI.HISTORY_TABLE, label="Date")

    if (movies and not episodes):
        GUI.add_table_column(parent=UI.HISTORY_TABLE, label="Movie")
    elif (episodes and not movies):
        GUI.add_table_column(parent=UI.HISTORY_TABLE, label="Show")
    elif (movies and episodes):    
        GUI.add_table_column(parent=UI.HISTORY_TABLE, label="Show / Movie")
        
    if (episodes):
        GUI.add_table_column(parent=UI.HISTORY_TABLE, label="Season")
        GUI.add_table_column(parent=UI.HISTORY_TABLE, label="Number")
        GUI.add_table_column(parent=UI.HISTORY_TABLE, label="Episode title")
        

def BuildUserInterface():

    GUI.create_context()
    GUI.create_viewport(title='Backup Trakt for Me', width=UI.VIEWPORT_MIN_WIDTH, height=UI.VIEWPORT_MIN_HEIGHT)

    with GUI.window(tag=UI.MAIN_WINDOW, no_collapse=True, no_move=True, show=True, no_title_bar=True, width=GUI.get_viewport_width(), height=GUI.get_viewport_height()):
        with GUI.tab_bar():
            with GUI.tab(tag=UI.BACKUP_TAB, label="Backup"):
                GUI.add_spacer(height=20)
                with GUI.group(horizontal=True):
                    GUI.add_button(tag=UI.BACKUP, label="Backup Trakt", callback=BackupTrakt, width=GUI.get_item_width(UI.MAIN_WINDOW) * 0.3)
                
                GUI.add_text()
                GUI.add_separator()
                with GUI.group(horizontal=True, horizontal_spacing=50):
                    media = ("All", "Episodes", "Movies")
                    GUI.add_combo(media, default_value=media[0], tag=UI.TYPE_COMBO, label="Media", height_mode=GUI.mvComboHeight_Small, width=200, callback=UpdateHistoryTable)
                    GUI.add_combo(tag=UI.YEAR_COMBO, label="Year", height_mode=GUI.mvComboHeight_Small, width=200, callback=UpdateHistoryTable)

                GUI.add_separator()
                GUI.add_spacer(height=20)

                # History table
                with GUI.table(tag=UI.HISTORY_TABLE, header_row=True, no_host_extendX=True, delay_search=True,
                            borders_innerH=True, borders_outerH=True, borders_innerV=True,
                            borders_outerV=True, context_menu_in_body=True, row_background=True,
                            policy=GUI.mvTable_SizingFixedFit, height=200,
                            scrollY=True, scrollX=True, clipper=True):
                
                    AddColumnsToTable(True, True)

            with GUI.tab(label="Settings"):
                GUI.add_spacer(height=20)
                GUI.add_input_text(tag=UI.CLIENT_ID, no_spaces=True, default_value="Your client ID", label="Client ID")
                GUI.add_separator()
                GUI.add_input_text(tag=UI.CLIENT_SECRET, no_spaces=True, default_value="Your client secret", label="Client Secret")

                
                GUI.add_button(tag=UI.AUTHORIZE, label="Authorize User", callback=AuthorizeUser)

                GUI.add_spacer(height=20)
                GUI.add_separator()
                GUI.add_input_text(tag=UI.ACCES_TOKEN, no_spaces=True, enabled=False, default_value="It will show user refresh token once authorized", label="Access Token")
                GUI.add_separator()
                GUI.add_input_text(tag=UI.REFRESH_TOKEN, no_spaces=True, enabled=False, default_value="It will show user refresh token once authorized", label="Refresh Token")

                GUI.add_button(tag=UI.REFRESH, label="Refresh Token", callback=RefreshUserToken)

                GUI.add_spacer(height=20)
                GUI.add_input_text(tag=UI.BACKUP_FOLDER, default_value='.', enabled=False, label= "Backup Folder")
                GUI.add_button(tag=UI.SELECT_FOLDER, label="Select backup folder", callback=lambda: GUI.show_item(UI.FOLDER_DIALOG))
                GUI.add_file_dialog(tag=UI.FOLDER_DIALOG, label="Select backup folder...", directory_selector=True, show=False, callback=SelectBackupFolder, cancel_callback=SelectBackupFolderCancelled, width=700, height=400)

            
        GUI.add_spacer(height=20)
        with GUI.group(horizontal=True):
            GUI.add_button(tag=UI.SCROLL, label="Scroll to bottom", callback=ScrollDown)
            GUI.add_button(tag=UI.CLEAR, label="Clear", callback=ClearConsole)

        with GUI.child_window(tag=UI.CONSOLE_WINDOW, label="Log"):
            pass

parser = argparse.ArgumentParser(prog="Backup Trakt for Me")

parser.add_argument('--no_user_interface', action='store_false', help='disables user interface (use this to backup periodically with an automatic task)')

args = parser.parse_args()

useUI = args.no_user_interface

if (useUI):
    BuildUserInterface()

    logger = Logger(useUI, "UI")
    controller = AppController(useUI)
    
    UpdateUISettings()
    UpdateUIYearsCombo()
    UpdateHistoryTable()

    GUI.setup_dearpygui()
    GUI.set_viewport_resizable(True)
    GUI.set_viewport_min_width(UI.VIEWPORT_MIN_WIDTH)
    GUI.set_viewport_min_height(UI.VIEWPORT_MIN_HEIGHT)
    GUI.set_primary_window(UI.MAIN_WINDOW, True)
    GUI.show_viewport()
    GUI.start_dearpygui()
    GUI.destroy_context()

else:
    controller = AppController(useUI)
    controller.BackupTrakt()