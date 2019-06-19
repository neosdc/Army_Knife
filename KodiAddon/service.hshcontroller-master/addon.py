import time
import os
import xbmc
import xbmcaddon
import xbmcvfs
import xbmcgui
import platform
import socket
from uuid import getnode as get_mac

import requests
import hashlib
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

controlroom_address = ""
controlroom_port = 0
ping_interval = float(100)
download_path = "/tmp/xbmcdownload"

formats = {"Video" : ["AVI", "MPG", "WMV", "ASF", "FLV", "MKV", "MKA", "MP4", "RM", "OGM", "3GP"], "Audio" : ["OGG", "MP3", "WAV", "MP2", "FLAC"], "Picture" : ["BMP", "JPG", "GIF", "ICO", "PCX", "TGA", "PNG", "MNG"]}

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def getFileMd5(filename):
    hash_md5 = hashlib.md5()
    try:
        with open(filename, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except:
        return None

def get_disk_usage():
    statvfs = os.statvfs(download_path)
    return statvfs.f_frsize * statvfs.f_bavail

def write_download_file(resp, path, filename):
    with open(os.path.join(path, filename), 'wb') as downloadFile:
        for fileChunk in resp:
            downloadFile.write(fileChunk)

def send_get_ControlRoom(func, payload, stream=False):
    xbmc.log("hsh! send_get_ControlRoom %s" % func, level=xbmc.LOGNOTICE)
    r = requests.get('https://{}:{}/xbmccontrol/api/{}'.format(controlroom_address, controlroom_port, func), params=payload, stream=stream, verify=False)
    response = r.json()
    xbmc.log("hsh! response %s" % response, level=xbmc.LOGNOTICE)
    return response

class KodiMonitor(xbmc.Monitor):
    def onSettingsChanged(self):
        xbmc.Monitor.onSettingsChanged(self)
        global controlroom_address, controlroom_port, ping_interval, download_path
        controlroom_address = addon.getSetting('controlroom_address')
        controlroom_port = addon.getSetting('controlroom_port')
        ping_interval = float(addon.getSetting('ping_interval'))
        download_path = addon.getSetting('download_folder')

        xbmc.log("hsh! onSettingsChanged", level=xbmc.LOGNOTICE)

    def onNotification(self, sender, method, data):
        xbmc.Monitor.onNotification(self, sender, method, data)
        xbmc.log("hsh! onNotification sender:{} method:{} data:{}".format(sender, method, data), level=xbmc.LOGNOTICE)

if __name__ == '__main__':
    monitor = KodiMonitor()

    addon = xbmcaddon.Addon()
    controlroom_address = addon.getSetting('controlroom_address')
    controlroom_port = addon.getSetting('controlroom_port')
    ping_interval = float(addon.getSetting('ping_interval'))
    download_path = addon.getSetting('download_folder')
    display_name = addon.getSetting('display_name')
    #xbmc.log("hsh! has been started! %s" % time.time(), level=xbmc.LOGNOTICE)

    try:
        osInfo = "{} {}".format(platform.system(), platform.platform())
    except Exception as e:
        xbmc.log("Unexpected error osInfo:{}".format(e), level=xbmc.LOGNOTICE)
        osInfo = ""
    ipAddress = get_ip_address()
    macAddress = "".join(c + ":" if i % 2 else c for i, c in enumerate(hex(get_mac())[2:-1].zfill(12)))[:-1]
    try:
        import cpuinfo
        cpuBrand = "{} {} {}".format(platform.machine(), platform.processor(), cpuinfo.get_cpu_info()['brand'])
    except Exception as e:
        xbmc.log("Unexpected error cpuBrand:{}".format(e), level=xbmc.LOGNOTICE)
        cpuBrand = "{} {}".format(platform.machine(), platform.processor())
    xbmc_version = xbmc.getInfoLabel("System.BuildVersion")
    if display_name == "default":
        name = socket.gethostname()
    else:
        name = display_name

    xbmc.log("hsh! - osInfo : %s" % osInfo, level=xbmc.LOGNOTICE)
    xbmc.log("hsh! - ipAddress : %s" % ipAddress, level=xbmc.LOGNOTICE)
    xbmc.log("hsh! - macAddress : %s" % macAddress, level=xbmc.LOGNOTICE)
    xbmc.log("hsh! - cpuBrand : %s" % cpuBrand, level=xbmc.LOGNOTICE)
    xbmc.log("hsh! - xbmc_version : %s" % xbmc_version, level=xbmc.LOGNOTICE)

    initialized = False

    hostIdx = -1

    while not monitor.abortRequested():
        if not initialized:
            try:
                payload = {'name': name, 'mac': macAddress, 'ip' : ipAddress, 'os': osInfo, 'app' : xbmc_version, 'dv' : cpuBrand}
                response = send_get_ControlRoom('welcome', payload)
                hostIdx = response['idx']                
            except Exception as e:
                xbmc.log("Unexpected error:{}".format(e), level=xbmc.LOGNOTICE)
                dialog = xbmcgui.Dialog()
                dialog.notification('HomeSweetHome', 'Fail to connect Control Server.', xbmcgui.NOTIFICATION_INFO, 5000)
                continue
            else:
                initialized = True

        if initialized:
            try:
                payload = {'idx':hostIdx}
                response = send_get_ControlRoom('ping', payload)

                if response['action'] == "downloadAndPlay":
                    downloadedFileFormats = {"Video":0, "Audio":0, "Picture":0}
                    xbmc.log("hsh! action command downloadAndPlay has detected", level=xbmc.LOGNOTICE)

                    payload = {'idx':response['action_param']}
                    response = send_get_ControlRoom('mediabunch', payload, True)
                    
                    if not xbmcvfs.exists(download_path):
                        xbmc.log("hsh! download directory not found.", level=xbmc.LOGNOTICE)
                        xbmcvfs.mkdir(download_path)

                    freespace = get_disk_usage()
                    needspace = 0
                    for targetfile in response['medias']:
                        needspace += targetfile['size']

                    if freespace < needspace:
                        xbmc.log("hsh! Not Enough Disk Space.", level=xbmc.LOGNOTICE)
                        dialog = xbmcgui.Dialog()
                        dialog.notification('HomeSweetHome', 'Not Enough Disk Space.', xbmcgui.NOTIFICATION_INFO, 5000)
                        continue

                    for targetfile in response['medias']:
                        xbmc.log("hsh! targetFile {}".format(targetfile), level=xbmc.LOGNOTICE)
                        fname, ext = os.path.splitext(targetfile['name'])

                        for key, fmt in formats.iteritems():
                            if ext in fmt:
                                downloadedFileFormats[key] = downloadedFileFormats[key] + 1

                        if getFileMd5(os.path.join(download_path, str(targetfile['idx']) + ext)) != targetfile['md5']:
                            xbmc.log("hsh! No matched File Hash {}".format(targetfile['idx']), level=xbmc.LOGNOTICE)
                            payload = {'idx':targetfile['idx']}
                            write_download_file(
                                requests.get('https://{}:{}/xbmccontrol/api/mediadownload'.format(controlroom_address, controlroom_port), params=payload, stream=True, verify=False),
                                download_path,
                                str(targetfile['idx']) + ext)
                    dialog = xbmcgui.Dialog()
                    dialog.notification('HomeSweetHome', 'Command [Download&Play].', xbmcgui.NOTIFICATION_INFO, 5000)

                    selectedCategory = max(downloadedFileFormats, key=downloadedFileFormats.get)
                    #https://kodi.wiki/view/List_of_built-in_functions

                    if selectedCategory == "Picture":
                        xbmc.executebuiltin('SlideShow("{0}")'.format(download_path))
                    else:
                        xbmc.executebuiltin('xbmc.PlayMedia("{0}","isdir")'.format(download_path))
                        xbmc.executebuiltin('xbmc.PlayerControl(RepeatAll)')
                        xbmc.executebuiltin("Action(Fullscreen)")
                elif response['action'] == "restart":
                    payload = {'idx':hostIdx}
                    response = send_get_ControlRoom('bye', payload)                    
                    xbmc.executebuiltin('RestartApp')
                elif response['action'] == "quit":
                    payload = {'idx':hostIdx}
                    response = send_get_ControlRoom('bye', payload)
                    xbmc.executebuiltin('Quit')
                elif response['action'] == "reboot":
                    payload = {'idx':hostIdx}
                    response = send_get_ControlRoom('bye', payload)
                    xbmc.executebuiltin('Reboot')
                elif response['action'] == "powerdown":
                    payload = {'idx':hostIdx}
                    response = send_get_ControlRoom('bye', payload)
                    xbmc.executebuiltin('Powerdown')
                elif response['action'] == "stop":
                    payload = {'idx':hostIdx}
                    xbmc.executebuiltin('xbmc.PlayerControl(Stop)')
                elif response['action'] == "update":
                    response = send_get_ControlRoom('addonversion', {})
                    if response['code'] == 1:
                        if addon.getAddonInfo('version') != response['version']:
                            write_download_file(
                                requests.get('https://{}:{}/xbmccontrol/api/addondownload'.format(controlroom_address, controlroom_port), stream=True, verify=False),
                                download_path,
                                'KodiAddon.zip')
                            #xbmc.executebuiltin('ActivateWindow(addons://install/)')
                            response = send_get_ControlRoom('bye', payload)
                            dialog = xbmcgui.Dialog()
                            dialog.notification('HomeSweetHome', 'Update Detected!', xbmcgui.NOTIFICATION_INFO, 5000)
                    break
            except Exception as e:
                xbmc.log("Unexpected error:{}".format(e), level=xbmc.LOGNOTICE)
                dialog = xbmcgui.Dialog()
                dialog.notification('HomeSweetHome', 'Fail to connect Control Server.', xbmcgui.NOTIFICATION_INFO, 5000)
                pass
        if monitor.waitForAbort(ping_interval):
            break
