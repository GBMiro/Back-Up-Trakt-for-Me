from AppController import AppController
import Utils.UI as UI
import dearpygui.dearpygui as GUI

def BackupHistory(sender, app_data, user_data):
    controller.BackupWatchedHistory()

GUI.create_context()
GUI.create_viewport(title='Backup Trakt for Me', width=700, height=500)

with GUI.window(tag=UI.MAIN_WINDOW, no_collapse=True, no_move=True, show=True, no_title_bar=True, width=GUI.get_viewport_width(), height=GUI.get_viewport_height()):
    with GUI.tab_bar():
        with GUI.tab(tag=UI.BACKUP_TAB, label="Backup/Restore"):
            GUI.add_text()
            GUI.add_button(tag=UI.BACKUP_BUTTON, label="Backup history", callback=BackupHistory)
            GUI.add_text()

        with GUI.tab(label="Trakt API Settings"):
            GUI.add_text("API Key", show_label=True)
            GUI.add_input_text(tag=UI.CLIENT_ID, default_value="Your client ID")
            GUI.add_separator()
            GUI.add_text("Client Secret", show_label=True)
            GUI.add_input_text(tag=UI.CLIENT_SECRET, default_value="Your client secret")
            GUI.add_separator()
            GUI.add_text("Acces Token", show_label=True)
            GUI.add_input_text(tag=UI.ACCES_TOKEN, default_value="Your access token")
            GUI.add_separator()
            GUI.add_text("Refresh Token", show_label=True)
            GUI.add_input_text(tag=UI.REFRESH_TOKEN, default_value="Your refresh token")
            GUI.add_text()

            with GUI.group(horizontal=True):
                authorizeButton = GUI.add_button(tag=UI.AUTHORIZE_BUTTON, label="Authorize User")
                refreshButton = GUI.add_button(tag=UI.REFRESH_BUTTON, label="Refresh Token")
                saveCongig = GUI.add_button(tag=UI.SAVE_BUTTON, label="Save")
            
        GUI.add_text(parent=UI.MAIN_WINDOW)
        GUI.add_text("Console", parent=UI.MAIN_WINDOW)


        with GUI.child_window(tag=UI.CONSOLE_WINDOW, label="Log", parent=UI.MAIN_WINDOW, tracked=True):
            pass

def LoadTraktSettings():
    GUI.set_value(UI.CLIENT_ID, controller.GetClientID())
    GUI.set_value(UI.CLIENT_SECRET, controller.GetClientSecret())
    GUI.set_value(UI.ACCES_TOKEN, controller.GetAccessToken())
    GUI.set_value(UI.REFRESH_TOKEN, controller.GetRefreshToken())


controller = AppController()
LoadTraktSettings()

GUI.setup_dearpygui()
GUI.set_viewport_resizable(False)
GUI.set_primary_window(UI.MAIN_WINDOW, True)
GUI.show_viewport()
GUI.start_dearpygui()
GUI.destroy_context()