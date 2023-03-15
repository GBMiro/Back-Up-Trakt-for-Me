from AppController import AppController
from Utils.Logger import Logger
import Utils.UI as UI
import dearpygui.dearpygui as GUI

# Trakt configuration functions

def AuthorizeUser(sender, app_data, user_data):
    id = GUI.get_value(UI.CLIENT_ID)
    secret = GUI.get_value(UI.CLIENT_SECRET)
    controller.SetTraktConfig(id, secret)
    controller.AuthorizeTraktUser()

def RefreshUserToken(sender, app_data, user_data):
    pass

# Application functions

def BackupHistory(sender, app_data, user_data):
    controller.BackupWatchedHistory()
    UpdateHistoryView()

def ClearConsole(sender, app_data, user_data):
    logger.Clear()

def ScrollDown(sender, app_data, user_data):
    logger.ScrollToBottom()

def UpdateHistoryView():
    GUI.delete_item(UI.HISTORY_TABLE, children_only=True, slot=1)
    data = controller.GetHistoryData()

    for play in data:
        type = play['type']
        id = play['play_ID']
        episode = "-" if type == 'movie' else play['Episode']
        season = "-" if type == 'movie' else play['Season']
        name = play['Title']
        date = play['Date']
        episodeTitle = "-" if type == 'movie' else play['Episode Title']

        with GUI.table_row(parent=UI.HISTORY_TABLE):
            GUI.add_text(id)
            GUI.add_text(date)
            GUI.add_text(name)
            GUI.add_text(season)
            GUI.add_text(episode)
            GUI.add_text(episodeTitle)
            
    logger.ShowMessage("Showing {} plays from last database backup".format(len(data)))

GUI.create_context()
GUI.create_viewport(title='Backup Trakt for Me', width=UI.VIEWPORT_MIN_WIDTH, height=UI.VIEWPORT_MIN_HEIGHT)

with GUI.window(tag=UI.MAIN_WINDOW, no_collapse=True, no_move=True, show=True, no_title_bar=True, width=GUI.get_viewport_width(), height=GUI.get_viewport_height()):
    with GUI.tab_bar():
        with GUI.tab(tag=UI.BACKUP_TAB, label="Backup"):
            GUI.add_text()
            GUI.add_button(tag=UI.BACKUP_BUTTON, label="Backup history", callback=BackupHistory, width=GUI.get_item_width(UI.MAIN_WINDOW) * 0.3)
            GUI.add_text()
            GUI.add_button(tag=UI.LOAD_BACKUP_BUTTON, label="Show last backup info", callback=UpdateHistoryView, width=GUI.get_item_width(UI.MAIN_WINDOW) * 0.3)
            GUI.add_text()

            # BACKUP LIST
            with GUI.table(tag=UI.HISTORY_TABLE, header_row=True, no_host_extendX=True, delay_search=True,
                        borders_innerH=True, borders_outerH=True, borders_innerV=True,
                        borders_outerV=True, context_menu_in_body=True, row_background=True,
                        policy=GUI.mvTable_SizingFixedFit, height=200,
                        scrollY=True, scrollX=True, clipper=True):
                
                GUI.add_table_column(label="Play ID")
                GUI.add_table_column(label="Watched at")
                GUI.add_table_column(label="Show / Movie")
                GUI.add_table_column(label="Season")
                GUI.add_table_column(label="Episode")
                GUI.add_table_column(label="Title")

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
                authorizeButton = GUI.add_button(tag=UI.AUTHORIZE_BUTTON, label="Authorize User", callback=AuthorizeUser)
                refreshButton = GUI.add_button(tag=UI.REFRESH_BUTTON, label="Refresh Token", callback=RefreshUserToken)
         
    with GUI.group():
        GUI.add_text("Console", parent=UI.MAIN_WINDOW)
        GUI.add_separator(parent=UI.MAIN_WINDOW)

    with GUI.group(horizontal=True):
        GUI.add_button(tag=UI.SCROLL_BUTTON, label="Scroll to bottom", callback=ScrollDown)
        GUI.add_button(tag=UI.CLEAR_BUTTON, label="Clear", callback=ClearConsole)

    with GUI.child_window(tag=UI.CONSOLE_WINDOW, label="Log"):
        pass

def LoadTraktSettings():
    GUI.set_value(UI.CLIENT_ID, controller.GetClientID())
    GUI.set_value(UI.CLIENT_SECRET, controller.GetClientSecret())
    GUI.set_value(UI.ACCES_TOKEN, controller.GetAccessToken())
    GUI.set_value(UI.REFRESH_TOKEN, controller.GetRefreshToken())
    logger.ShowMessage("Trakt settings updated in UI")

logger = Logger(True, "UI")
controller = AppController(True)
LoadTraktSettings()
UpdateHistoryView()

GUI.setup_dearpygui()
GUI.set_viewport_resizable(True)
GUI.set_viewport_min_width(UI.VIEWPORT_MIN_WIDTH)
GUI.set_viewport_min_height(UI.VIEWPORT_MIN_HEIGHT)
GUI.set_primary_window(UI.MAIN_WINDOW, True)
GUI.show_viewport()
GUI.start_dearpygui()
GUI.destroy_context()