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
    UpdateUITraktSettings()

def RefreshUserToken(sender, app_data, user_data):
    pass

# Application functions

def BackupHistory():
    controller.BackupWatchedHistory()
    UpdateHistoryTable(UI.SHOW_HISTORY)

def ClearConsole():
    logger.Clear()

def ScrollDown():
    logger.ScrollToBottom()

def UpdateUITraktSettings():
    GUI.set_value(UI.CLIENT_ID, controller.GetClientID())
    GUI.set_value(UI.CLIENT_SECRET, controller.GetClientSecret())
    GUI.set_value(UI.ACCES_TOKEN, controller.GetAccessToken())
    GUI.set_value(UI.REFRESH_TOKEN, controller.GetRefreshToken())
    logger.ShowMessage("Trakt settings updated in UI")


def UpdateHistoryTable(sender):
    GUI.delete_item(UI.HISTORY_TABLE, children_only=True)
    AddColumnsToTable(sender)
    data, statusCode = controller.GetHistoryData(sender)

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


def AddColumnsToTable(sender):

    GUI.add_table_column(parent=UI.HISTORY_TABLE, label="Play ID")
    GUI.add_table_column(parent=UI.HISTORY_TABLE, label="Date")

    if (sender == UI.SHOW_MOVIES):
        GUI.add_table_column(parent=UI.HISTORY_TABLE, label="Movie")
    elif (sender == UI.SHOW_EPISODES):
        GUI.add_table_column(parent=UI.HISTORY_TABLE, label="Show")
    else:
        GUI.add_table_column(parent=UI.HISTORY_TABLE, label="Show / Movie")
    
    if (sender == UI.SHOW_EPISODES or sender == UI.SHOW_HISTORY):
        GUI.add_table_column(parent=UI.HISTORY_TABLE, label="Season")
        GUI.add_table_column(parent=UI.HISTORY_TABLE, label="Number")
        GUI.add_table_column(parent=UI.HISTORY_TABLE, label="Episode title")
        

def BuildUserInterface():

    GUI.create_context()
    GUI.create_viewport(title='Backup Trakt for Me', width=UI.VIEWPORT_MIN_WIDTH, height=UI.VIEWPORT_MIN_HEIGHT)

    with GUI.window(tag=UI.MAIN_WINDOW, no_collapse=True, no_move=True, show=True, no_title_bar=True, width=GUI.get_viewport_width(), height=GUI.get_viewport_height()):
        with GUI.tab_bar():
            with GUI.tab(tag=UI.BACKUP_TAB, label="Backup"):
                GUI.add_text()
                GUI.add_button(tag=UI.BACKUP, label="Backup history", callback=BackupHistory, width=GUI.get_item_width(UI.MAIN_WINDOW) * 0.3)
                GUI.add_text()
                GUI.add_separator()
                with GUI.group(horizontal=True, horizontal_spacing=50):
                    GUI.add_button(tag=UI.SHOW_HISTORY, label="Show all history", callback=UpdateHistoryTable, width=GUI.get_item_width(UI.MAIN_WINDOW) * 0.3)
                    GUI.add_button(tag=UI.SHOW_EPISODES, label="Show only episodes", callback=UpdateHistoryTable, width=GUI.get_item_width(UI.MAIN_WINDOW) * 0.3)
                    GUI.add_button(tag=UI.SHOW_MOVIES, label="Show only movies", callback=UpdateHistoryTable, width=GUI.get_item_width(UI.MAIN_WINDOW) * 0.3)

                GUI.add_separator()
                GUI.add_text()

                # History table
                with GUI.table(tag=UI.HISTORY_TABLE, header_row=True, no_host_extendX=True, delay_search=True,
                            borders_innerH=True, borders_outerH=True, borders_innerV=True,
                            borders_outerV=True, context_menu_in_body=True, row_background=True,
                            policy=GUI.mvTable_SizingFixedFit, height=200,
                            scrollY=True, scrollX=True, clipper=True):
                
                    AddColumnsToTable(UI.SHOW_HISTORY)

            with GUI.tab(label="Trakt API Settings"):
                GUI.add_text("Client ID", show_label=True)
                GUI.add_input_text(tag=UI.CLIENT_ID, no_spaces=True, default_value="Your client ID")
                GUI.add_separator()
                GUI.add_text("Client Secret", show_label=True)
                GUI.add_input_text(tag=UI.CLIENT_SECRET, no_spaces=True, default_value="Your client secret")
                GUI.add_separator()
                GUI.add_text("Access Token", show_label=True)
                GUI.add_text(tag=UI.ACCES_TOKEN, default_value="Your access token")
                GUI.add_separator()
                GUI.add_text("Refresh Token", show_label=True)
                GUI.add_text(tag=UI.REFRESH_TOKEN, default_value="Your refresh token")
                GUI.add_text()

                with GUI.group(horizontal=True):
                    GUI.add_button(tag=UI.AUTHORIZE, label="Authorize User", callback=AuthorizeUser)
                    GUI.add_button(tag=UI.REFRESH, label="Refresh Token", callback=RefreshUserToken)
            
        with GUI.group():
            GUI.add_text("Console", parent=UI.MAIN_WINDOW)
            GUI.add_separator(parent=UI.MAIN_WINDOW)

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
    
    UpdateUITraktSettings()
    UpdateHistoryTable(UI.SHOW_HISTORY)

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
    controller.BackupWatchedHistory()