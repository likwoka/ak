from cm.config import APP_ROOT


#The menu bar, each choice is a tuple (url, desc)
def Menu():
    return [('%shome' % APP_ROOT, _('Your Homepage')),
            ('%scase/' % APP_ROOT, _('Browse Cases')),
            ('%sincident/' % APP_ROOT, _('Browse Incidents')),
            ('%sstore/' % APP_ROOT, _('Browse Stores')),
            ('%sattachment/' % APP_ROOT, _('Browse Attachments')),
            ('%slogout' % APP_ROOT, _('Log Out'))]

def Report():
    return [('%sreport/top_10_incidents' % APP_ROOT, _('Top 10 Incidents'))]

def Pref():
    return [('%smypreference/' % APP_ROOT, _('Change Preference'))]

def AboutUs():
    return [('%saboutus' % APP_ROOT, _('About Us')),
            ('%sadmin' % APP_ROOT, _('Admin'))]
