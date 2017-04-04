#Expose this!!!
from cm.htmllib.internal_renderer import Grid, Message, Link, Pre
from cm.htmllib.form import AKForm
from cm.htmllib.mime import FileType
from cm.htmllib.list import List, AKCol
from cm.htmllib.tabpage import TabPage


from quixote.form.form import register_widget_class
from cm.htmllib.widget import *

register_widget_class(AKStringWidget)
register_widget_class(AKCheckboxWidget)
register_widget_class(AKIntWidget)
register_widget_class(AKFloatWidget)
register_widget_class(AKDateWidget)
register_widget_class(AKTimeWidget)
register_widget_class(AKTextWidget)
register_widget_class(AKFileWidget)
register_widget_class(AKRadiobuttonsWidget)
register_widget_class(AKSingleSelectWidget)
register_widget_class(AKPasswordWidget)

