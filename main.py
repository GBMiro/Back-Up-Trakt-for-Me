from AppController import AppController
import TraktAPI.TraktAPIUtils as TraktAPIUtils

def main():
    controller = AppController()
    statusCode = controller.AuthorizeTraktUser()
    if (statusCode == TraktAPIUtils.SUCCESS):
        statusCode = controller.BackupWatchedHistory()
        
    print (TraktAPIUtils.statusMessages[statusCode])
main()