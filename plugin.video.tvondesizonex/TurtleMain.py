'''
Created on Dec 27, 2011

@author: ajju
'''



import xbmcgui  # @UnresolvedImport
dialog = xbmcgui.Dialog()
dialog.ok('[B][COLOR green]ANNOUNCEMENT: [/COLOR][/B] TV on DESI ZONE v2 with new look available', 'To install, go to http://goo.gl/wri4dS', 'Install aj add-ons (new look) repository.', 'NOTE: Supported on XBMC Frodo or Later.')

try:
    import TurtlePlugin
except:
    import xbmcgui  # @UnresolvedImport
    dialog = xbmcgui.Dialog()
    dialog.ok('[B][COLOR red]ALERT: [/COLOR][/B] RESTART XBMC', 'A new update has recently installed or add-on reconfigured.', 'Please restart XBMC to reflect the changes.', 'You will not be able to access until restart.')

TurtlePlugin.start('plugin.video.tvondesizonex')
