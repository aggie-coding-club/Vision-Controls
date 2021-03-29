import webbrowser
import os, getpass


# ------------- WEB BROWSER -------------

def registerBrowsers():
    webbrowser.register("chrome", None, webbrowser.BackgroundBrowser("C://Program Files (x86)//Google//Chrome//Application//chrome.exe"))
    webbrowser.register("firefox", None, webbrowser.BackgroundBrowser("C://Program Files//Mozilla Firefox//firefox.exe"))
    webbrowser.register("chromeWSL", None, webbrowser.BackgroundBrowser("/mnt/c/Program Files (x86)/Google/Chrome/Application/chrome.exe"))
    webbrowser.register("firefoxWSL", None, webbrowser.BackgroundBrowser("/mnt/c/Program Files/Mozilla Firefox/firefox.exe"))
    webbrowser.register("chromeMac", None, webbrowser.BackgroundBrowser("open -a /Applications/Google\ Chrome.app"))
    
# open web browsers with specified url
def openChromeWin(url):
    webbrowser.get("chrome").open(url)

def openFirefoxWin(url):
    webbrowser.get("firefox").open(url)

def openChromeWSL(url):
    webbrowser.get("chromeWSL").open(url)

def openFirefoxWSL(url):
    webbrowser.get("firefoxWSL").open(url)





# --------------- GENERAL ---------------

def openProgram(path):
    os.startfile(path)

def openSpotify():
    username = getpass.getuser()
    os.startfile("C://Users//" + username + "//AppData//Roaming//Spotify//Spotify.exe")




# driver code
if __name__ == "__main__":
    registerBrowsers()
    # openFirefoxWin("www.google.com")
    # openSpotify()
