import xbmcgui  # @UnresolvedImport



def selectEvents(request_obj, response_obj):
    if not request_obj.get_data()['isLoginSuccess']:
        return
    d = xbmcgui.Dialog()
    index = d.select('Select events category:', ['Upcoming', 'Ongoing/Concluded', 'Archive 2013', 'Archive 2012', 'Archive 2011', 'Archive 2010'])
    if index == 0:
        request_obj.get_data()['target'] = 'upcoming'
    elif index == 1:
        request_obj.get_data()['target'] = 'concluded'
    elif index == 2:
        request_obj.get_data()['target'] = 'archive2013'
    elif index == 3:
        request_obj.get_data()['target'] = 'archive2012'
    elif index == 4:
        request_obj.get_data()['target'] = 'archive2011'
    elif index == 5:
        request_obj.get_data()['target'] = 'archive2010'
        

def empty(request_obj, response_obj):
    XBMCInterfaceUtils.displayDialogMessage('Series doesn\'t have childs', 'Error: Select match under this series.', 'Please go back.')
    
