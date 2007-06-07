# GDB Manager
# Version 6.5
# by Juce.

import wx
import wx.lib.colourselect as csel
import string, math, re
import sys, os, cStringIO

import palettelib, cpalettelib

VERSION, DATE = "6.5", "06/2007"
DEFAULT_PNG = os.getcwd() + "/default.png"
CONFIG_FILE = os.getcwd() + "/gdbm.cfg"
WINDOW_TITLE = "GDB Manager 6"
FRAME_WIDTH = 800
FRAME_HEIGHT = 830

DEFAULT_MASK = "mask.png"
MASK_COLORS = {
    "shirt":0x0000ff,
    "shorts":0xff0000,
    "socks":0x00ffff,
}

overlayPositions = {
    "wide-back":{
        "numbers":[220,46], 
        "chest-center":[85,60], 
        "chest-topright":[55,30], 
        "shorts-left":[120,205],
        "shorts-right":[40,205],
        "nameA-type1-top":[210,15],
        "nameB-type1-top":[225,15],
        "nameC-type1-top":[240,15],
        "nameA-type2-top":[205,15],
        "nameB-type2-top":[225,15],
        "nameC-type2-top":[237,15],
        "nameA-type3-top":[203,15],
        "nameB-type3-top":[225,15],
        "nameC-type3-top":[237,15],
        "nameA-type1-bottom":[210,110],
        "nameB-type1-bottom":[225,110],
        "nameC-type1-bottom":[240,110],
        "nameA-type2-bottom":[210,110],
        "nameB-type2-bottom":[225,110],
        "nameC-type2-bottom":[240,110],
        "nameA-type3-bottom":[210,110],
        "nameB-type3-bottom":[225,110],
        "nameC-type3-bottom":[240,110],
        "num-height":64,
        "shorts-num-height":32,
        "chest-num-height":32,
        "font-height":24,
     },
     "narrow-back":{
        "numbers":[245,46], 
        "chest-center":[109,60], 
        "chest-topright":[69,25], 
        "shorts-left":[120,205],
        "shorts-right":[40,205],
        "nameA-type1-top":[235,15],
        "nameB-type1-top":[250,15],
        "nameC-type1-top":[265,15],
        "nameA-type2-top":[230,15],
        "nameB-type2-top":[250,15],
        "nameC-type2-top":[262,15],
        "nameA-type3-top":[228,15],
        "nameB-type3-top":[250,15],
        "nameC-type3-top":[262,15],
        "nameA-type1-bottom":[235,110],
        "nameB-type1-bottom":[250,110],
        "nameC-type1-bottom":[265,110],
        "nameA-type2-bottom":[235,110],
        "nameB-type2-bottom":[250,110],
        "nameC-type2-bottom":[265,110],
        "nameA-type3-bottom":[235,110],
        "nameB-type3-bottom":[250,110],
        "nameC-type3-bottom":[265,110],
        "num-height":64,
        "shorts-num-height":32,
        "chest-num-height":32,
        "font-height":24,
     },
     "pes6-new":{
        "numbers":[380,26], 
        "chest-center":[149,40], 
        "chest-topright":[109,15], 
        "shorts-left":[235,130],
        "shorts-right":[100,130],
        "nameA-type1-top":[370,7],
        "nameB-type1-top":[385,7],
        "nameC-type1-top":[401,7],
        "nameA-type2-top":[365,7],
        "nameB-type2-top":[385,7],
        "nameC-type2-top":[399,7],
        "nameA-type3-top":[363,7],
        "nameB-type3-top":[385,7],
        "nameC-type3-top":[399,7],
        "nameA-type1-bottom":[370,70],
        "nameB-type1-bottom":[385,70],
        "nameC-type1-bottom":[401,70],
        "nameA-type2-bottom":[370,70],
        "nameB-type2-bottom":[385,70],
        "nameC-type2-bottom":[401,70],
        "nameA-type3-bottom":[370,70],
        "nameB-type3-bottom":[385,70],
        "nameC-type3-bottom":[401,70],
        "num-height":43,
        "shorts-num-height":18,
        "chest-num-height":18,
        "font-height":18,
     }
}

narrowBacks = [8]
wideBacks = [
    0,1,2,3,4,9,10,11,12,13,14,15,17,24,26,34,36,37,38,
    39,44,51,55,57,59,60,62,64,77,78,80,86,87,88,93,94,
    100,101,102,103,104,105,106,107,114
]
squashedWithLogo = [
    18,19,20,21,49,54,61,68,69,70,74,91,
    115,116,117,118,124,125,126,127,128,129,132,134,
    137,138,139,140,146,147,148
]

def getKitTemplateType(model):
    if int(model) in narrowBacks: return "narrow-back"
    if int(model) in wideBacks: return "wide-back"
    return "pes6-new"

def getBitmapWithPalette(imagefile, palfile, rect):
    # replace palette
    imageData = palettelib.usePalette(imagefile,palfile)
    # make the bitmap from data
    stream = cStringIO.StringIO(imageData)
    bmp = wx.BitmapFromImage( wx.ImageFromStream( stream ))
    return bmp.GetSubBitmap(rect)

def applyMask(bitmap, maskfile):
    maskImg = wx.Bitmap(maskfile).ConvertToImage()
    maskImg.InitAlpha()
    img = bitmap.ConvertToImage()
    if not img.HasAlpha(): img.InitAlpha()
    a,b = img.GetAlphaBuffer(), maskImg.GetAlphaData()
    #for i in range(len(a)): a[i] = min(a[i], b[i])
    #img.SetAlphaBuffer(a)
    img.SetAlphaBuffer(b)
    return img.ConvertToBitmap()

def applyColourMask(image, maskimage, color):
    alphaBuf = image.GetAlphaBuffer()
    maskImageBuf = maskimage.GetDataBuffer()
    cpalettelib.applyAlphaMask(alphaBuf,maskImageBuf,color)

def hasSamePalette(shirtPath, shortsPath):
    shirt = "%s\\all.png" % shirtPath
    if not os.path.exists(shirt):
        shirt = "%s\\shirt.png" % shirtPath
        if not os.path.exists(shirt):
            shirt = "%s\\all.bmp" % shirtPath
            if not os.path.exists(shirt):
                shirt = "%s\\shirt.bmp" % shirtPath
                if not os.path.exists(shirt):
                    return False
    shorts = "%s\\all.png" % shortsPath
    if not os.path.exists(shorts):
        shorts = "%s\\shorts.png" % shortsPath
        if not os.path.exists(shorts):
            shorts = "%s\\all.bmp" % shortsPath
            if not os.path.exists(shorts):
                shorts = "%s\\shorts.bmp" % shortsPath
                if not os.path.exists(shorts):
                    return False
    return palettelib.samePalette(shirt, shorts)

def getCommonDir(path,base):
    npath = os.path.normcase(path).split('\\')
    nbase = os.path.normcase(base).split('\\')
    common = [s for (s,i) in zip(npath,range(min(len(npath),len(nbase)))) if nbase[i]==s]
    return '\\'.join(common)

def makeRelativePath(path, base):
    commonDir = getCommonDir(path,base)
    if len(commonDir)==0:
        return path
    relPath = path[len(commonDir)+1:]
    baseRest = base[len(commonDir)+1:]
    if len(baseRest)>0:
        relPath = "%s%s" % ("../" * len(baseRest.split("\\")), relPath)
    return os.path.normcase(relPath)

def isNationalKit(teamId):
    return teamId < 64 or teamId > 203

"""
Read kit attributes from config.txt file
"""
def readAttributes(kit):
    # don't read again, if already done so
    if kit.attribRead:
        return

    # clear out the attributes dictionary
    kit.attributes.clear()

    #print "Reading attributes for %s" % kit.foldername
    path, kitKey = os.path.split(kit.foldername)
    # set goalkeeper flag
    if kitKey[0] == 'g':
        kit.isKeeper = True

    att, section = None, ""
    try:
        att = open("%s/%s" % (kit.foldername, "config.txt"))
        found = False
        for line in att:
            line = line.strip()
            #print "line: {%s}" % line

            # strip out the comment
            commentStarts = line.find("#")
            if commentStarts != -1:
                line = line[:commentStarts]

            if len(line.strip())==0:
                continue

            tok = line.split('=',2)
            if len(tok)==2:
                val = tok[1].strip()
                if val[0]=='"' and val[-1]=='"': val = val[1:-1]
                kit.attributes[tok[0].strip()] = val

        att.close()

    except IOError:
        # unable to read attributes. Ignore.
        if att != None:
            att.close()

    #print kit.attributes
    kit.attribRead = True


class RGBAColor:
    def __init__(self, color, alpha=-1):
        self.color = color
        self.alpha = alpha


"""
Utility method to construct wx.Color object 
from a RRGGBBAA string, as used in attrib.cfg files
"""
def MakeRGBAColor(str):
    r, g, b = int(str[0:2],16), int(str[2:4],16), int(str[4:6],16)
    try:
        a = int(str[6:8], 16)
        return RGBAColor(wx.Color(r,g,b), a)
    except:
        return RGBAColor(wx.Color(r,g,b), -1)


"""
Utility method for showing message box window
"""
def MessageBox(owner, title, text):
    dlg = wx.MessageDialog(owner, text, title, wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()

"""
A panel with colour select button, label, and edit control
"""
class KitColourSelect(wx.Panel):
    def __init__(self, parent, attribute, labelText, frame):
        wx.Panel.__init__(self, parent, -1)

        self.undef = wx.Color(0x99,0x99,0x99)
        self.att = attribute
        #self.label = wx.StaticText(self, -1, labelText, size=(120, -1), style=wx.ALIGN_RIGHT)
        #font = wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL)
        #self.label.SetFont(font)
        #self.label.SetSize(self.label.GetBestSize())

        ##########################
        self.label = wx.StaticText(self, -1, labelText, size=(180,-1), style=wx.ALIGN_RIGHT)
        self.label.SetBackgroundColour(wx.Colour(230,230,230))
        font = wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.label.SetFont(font)
        self.label.SetSize(self.label.GetBestSize())

        #self.choice = wx.Choice(self, -1, choices=[str(i) for i in items], size=(100,-1))
        #self.choice.SetSelection(0)
        #self.button = wx.Button(self, -1, "undef", size=(60,1))

        #self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        #self.sizer.Add(self.button, 0, wx.RIGHT | wx.EXPAND, border=10)
        #self.sizer.Add(self.label, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=10)
        #self.sizer.Add(self.choice, 0, wx.EXPAND)
        ##############################


        self.cs = csel.ColourSelect(self, -1, "", self.undef, size=(40,-1))
        self.edit = wx.TextCtrl(self, -1, "undefined", style=wx.TE_PROCESS_ENTER, validator=MyValidator(), size=(80,-1))
        self.edit.SetMaxLength(8)
        self.button = wx.Button(self, -1, "undef", size=(60, -1)) 
        self.frame = frame

        csSizer = wx.BoxSizer(wx.HORIZONTAL)
        csSizer.Add(self.cs, 0, wx.EXPAND)
        csSizer.Add(self.edit, 0, wx.EXPAND)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.button, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=10)
        sizer.Add(self.label, 0, wx.EXPAND)
        sizer.Add(csSizer, 0, wx.LEFT | wx.EXPAND, border=10)

        self.SetSizer(sizer)
        self.Layout()

        self.cs.Bind(csel.EVT_COLOURSELECT, self.OnSelectColour)
        self.edit.Bind(wx.EVT_TEXT_ENTER, self.OnEditColour)
        self.button.Bind(wx.EVT_BUTTON, self.OnUndef)


    def SetColour(self, color):
        self.cs.SetColour(color)
        self.edit.SetValue("%02X%02X%02X" % (color.Red(), color.Green(), color.Blue()))
        # update the kit panel
        try:
            self.frame.kitPanel.kit.attributes[self.att] = self.edit.GetValue()
            self.frame.kitPanel.Refresh()
        except AttributeError:
            pass
        except KeyError:
            pass

    def SetRGBAColour(self, rgba):
        color = rgba.color
        self.cs.SetColour(color)
        if rgba.alpha == -1:
            self.edit.SetValue("%02X%02X%02X" % (color.Red(), color.Green(), color.Blue()))
        else:
            self.edit.SetValue("%02X%02X%02X%02X" % (color.Red(), color.Green(), color.Blue(), rgba.alpha))
        # update the kit panel
        try:
            self.frame.kitPanel.kit.attributes[self.att] = self.edit.GetValue()
            self.frame.kitPanel.Refresh()
        except AttributeError:
            pass
        except KeyError:
            pass


    def ClearColour(self):
        self.cs.SetColour(self.undef)
        self.edit.SetValue("undefined")
        # update the kit panel
        try:
            del self.frame.kitPanel.kit.attributes[self.att]
            self.frame.kitPanel.Refresh()
        except AttributeError:
            pass
        except KeyError:
            pass


    """
    Sets attribute to newly selected color
    """
    def OnSelectColour(self, event):
        self.SetColour(event.GetValue())

        # add to modified list
        self.frame.addKitToModified()


    """
    Verifies manually edited color and sets attribute
    """
    def OnEditColour(self, event):
        text = self.edit.GetValue()
        # add padding zeroes, if needed
        if len(text) < 6:
            text = "%s%s" % ('0'*(6-len(text)), text)

        # attempt to set the color
        color = self.undef
        try:
            color = MakeRGBAColor(text)
            self.SetRGBAColour(color)
        except:
            self.ClearColour()

        # add to modified list
        self.frame.addKitToModified()


    """
    Removes color definition from attributes
    """
    def OnUndef(self, event):
        self.ClearColour()

        # add to modified list
        self.frame.addKitToModified()


class MyValidator(wx.PyValidator):
    def __init__(self):
        wx.PyValidator.__init__(self)
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        return MyValidator()

    def Validate(self, win):
        tc = self.GetWindow()
        val = tc.GetValue()

        for x in val:
            if x not in string.hexdigits:
                return False

        return True

    def OnChar(self, event):
        key = event.KeyCode()

        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()
            return

        if chr(key) in string.hexdigits:
            event.Skip()
            return

        if not wx.Validator_IsSilent():
            wx.Bell()

        # Returning without calling even.Skip eats the event before it
        # gets to the text control
        return

"""
A drop-down list with label
"""
class MyKeyList(wx.Panel):
    def __init__(self, parent, labelText, items, frame):
        wx.Panel.__init__(self, parent, -1)
        self.frame = frame
        self.label = wx.StaticText(self, -1, labelText, size=(160,-1), style=wx.ALIGN_RIGHT)
        self.label.SetBackgroundColour(wx.Colour(230,230,230))
        font = wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.label.SetFont(font)
        self.label.SetSize(self.label.GetBestSize())

        self.choice = wx.Choice(self, -1, choices=[str(i) for i in items], size=(140,-1))
        self.choice.SetSelection(0)

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.label, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=10)
        self.sizer.Add(self.choice, 0, wx.EXPAND)

        # by default the kit panel is not refreshed on selection change
        self.refreshOnChange = False

        # bind events
        self.choice.Bind(wx.EVT_CHOICE, self.OnSelect)

        self.SetSizer(self.sizer)
        self.Layout()


    def OnSelect(self, event):
        selection = event.GetString()
        print "Shorts selected: %s" % selection
        self.frame.kitPanel.kit.shortsKey = selection
        # bind kit to shorts-kit
        kit = self.choice.GetClientData(self.choice.GetSelection())
        self.frame.shortsNumLocation.kit = kit
        self.frame.shortsNumLocation.SetStringSelection()
        self.frame.numpal.SetStringSelection()
        self.frame.kitPanel.Refresh()


"""
A drop-down list with label
"""
class MyList(wx.Panel):
    def __init__(self, parent, attribute, labelText, items, frame, kit=None):
        wx.Panel.__init__(self, parent, -1)
        self.frame = frame
        self.kit = kit
        self.att = attribute
        self.label = wx.StaticText(self, -1, labelText, size=(200,-1), style=wx.ALIGN_RIGHT)
        self.label.SetBackgroundColour(wx.Colour(230,230,230))
        font = wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.label.SetFont(font)
        self.label.SetSize(self.label.GetBestSize())

        self.choice = wx.Choice(self, -1, choices=[str(i) for i in items], size=(100,-1))
        self.choice.SetSelection(0)
        self.button = wx.Button(self, -1, "undef", size=(60,1))

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.button, 0, wx.RIGHT | wx.EXPAND, border=10)
        self.sizer.Add(self.label, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=10)
        self.sizer.Add(self.choice, 0, wx.EXPAND)

        # by default the kit panel is not refreshed on selection change
        self.refreshOnChange = False

        # bind events
        self.choice.Bind(wx.EVT_CHOICE, self.OnSelect)
        self.button.Bind(wx.EVT_BUTTON, self.OnUndef)

        self.SetSizer(self.sizer)
        self.Layout()


    def getKit(self):
        kit = self.kit
        if kit == None: kit = self.frame.kitPanel.kit
        return kit


    def SetStringSelection(self, str=None):
        kit = self.getKit()
        if str == None:
            try: str = kit.attributes[self.att]
            except KeyError: str = "undefined"
        self.choice.SetStringSelection(str)
        kit.attributes[self.att] = str
        if self.refreshOnChange:
            self.frame.kitPanel.Refresh()


    def SetUndef(self):
        kit = self.getKit()
        self.choice.SetSelection(0)
        try:
            del kit.attributes[self.att] 
        except AttributeError:
            pass
        except KeyError:
            pass
        if self.refreshOnChange:
            self.frame.kitPanel.Refresh()


    def OnSelect(self, event):
        kit = self.getKit()
        selection = event.GetString()
        index = self.choice.GetSelection()
        if index == 0:
            # first item should always be "undefined"
            self.SetUndef()
        else:
            self.SetStringSelection(selection)

        # add kit to modified set
        self.frame.addKitToModified(kit)


    def OnUndef(self, event):
        kit = self.getKit()
        self.SetUndef()

        # add kit to modified set
        self.frame.addKitToModified(kit)

"""
A text field choice with label
"""
class MyTextField(wx.Panel):
    def __init__(self, parent, attribute, labelText, value, rootPath, frame, kit=None):
        wx.Panel.__init__(self, parent, -1)
        self.rootPath = rootPath
        self.frame = frame
        self.kit = kit
        self.att = attribute
        self.label = wx.StaticText(self, -1, labelText, size=(100,-1), style=wx.ALIGN_RIGHT)
        self.label.SetBackgroundColour(wx.Colour(230,230,230))
        font = wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.label.SetFont(font)
        self.label.SetSize(self.label.GetBestSize())

        self.text = wx.TextCtrl(self, -1, "", size=(200,-1))
        self.button = wx.Button(self, -1, "undef", size=(60,1))

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.button, 0, wx.RIGHT | wx.EXPAND, border=10)
        self.sizer.Add(self.label, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=10)
        self.sizer.Add(self.text, 0, wx.EXPAND)

        # by default the kit panel is not refreshed on selection change
        self.refreshOnChange = False

        # bind events
        #self.text.Bind(wx.EVT_CHOICE, self.OnSelect)
        self.button.Bind(wx.EVT_BUTTON, self.OnUndef)
        self.text.Bind(wx.EVT_TEXT, self.OnTextChange)

        self.SetSizer(self.sizer)
        self.Layout()


    def getKit(self):
        kit = self.kit
        if kit == None: kit = self.frame.kitPanel.kit
        return kit


    def SetStringSelection(self, str):
        kit = self.getKit()
        self.text.SetValue(str)
        kit.attributes[self.att] = str
        if self.refreshOnChange:
            self.frame.kitPanel.Refresh()

    def SetUndef(self):
        kit = self.getKit()
        self.text.SetValue("")
        try:
            del kit.attributes[self.att] 
        except AttributeError:
            pass
        except KeyError:
            pass
        if self.refreshOnChange:
            self.frame.kitPanel.Refresh()

    def OnUndef(self, event):
        kit = self.getKit()
        self.SetUndef()

        # add kit to modified set
        self.frame.addKitToModified(kit)

    def OnTextChange(self, event):
        kit = self.getKit()
        if kit != None:
            oldVal = kit.attributes.get(self.att,"")
            newVal = self.text.GetValue()
            if newVal != oldVal:
                #print "Description modified: old={%s}, new={%s}" % (oldVal,newVal)
                kit.attributes[self.att] = newVal
                # add kit to modified set
                self.frame.addKitToModified(kit)


"""
A file choice with label
"""
class MyNumbersFile(wx.Panel):
    def __init__(self, parent, attribute, labelText, value, rootPath, frame, kit=None):
        wx.Panel.__init__(self, parent, -1)
        self.rootPath = rootPath
        self.frame = frame
        self.kit = kit
        self.att = attribute
        self.label = wx.StaticText(self, -1, labelText, size=(100,-1), style=wx.ALIGN_RIGHT)
        self.label.SetBackgroundColour(wx.Colour(230,230,230))
        font = wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.label.SetFont(font)
        self.label.SetSize(self.label.GetBestSize())

        self.text = wx.TextCtrl(self, -1, "", size=(170,-1))
        self.text.SetEditable(False)
        self.button = wx.Button(self, -1, "undef", size=(60,1))
        self.fileButton = wx.Button(self, -1, "...", size=(30,1))

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.button, 0, wx.RIGHT | wx.EXPAND, border=10)
        self.sizer.Add(self.label, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=10)
        self.sizer.Add(self.text, 0, wx.EXPAND)
        self.sizer.Add(self.fileButton, 0, wx.EXPAND)

        # by default the kit panel is not refreshed on selection change
        self.refreshOnChange = False

        # bind events
        #self.text.Bind(wx.EVT_CHOICE, self.OnSelect)
        self.button.Bind(wx.EVT_BUTTON, self.OnUndef)
        self.fileButton.Bind(wx.EVT_BUTTON, self.OnChooseFile)

        self.SetSizer(self.sizer)
        self.Layout()


    def getKit(self):
        kit = self.kit
        if kit == None: kit = self.frame.kitPanel.kit
        return kit


    def SetStringSelection(self, str):
        kit = self.getKit()
        self.text.SetValue(str)
        kit.attributes[self.att] = str
        if self.refreshOnChange:
            self.frame.kitPanel.Refresh()

    def SetUndef(self):
        kit = self.getKit()
        self.text.SetValue("")
        try:
            del kit.attributes[self.att] 
        except AttributeError:
            pass
        except KeyError:
            pass
        if self.refreshOnChange:
            self.frame.kitPanel.Refresh()

    def OnUndef(self, event):
        kit = self.getKit()
        self.SetUndef()

        # add kit to modified set
        self.frame.addKitToModified(kit)

    def OnChooseFile(self, event):
        wildcard = "PNG images (*.png)|*.png|" \
                   "BMP images (*.bmp)|*.bmp"

        kit = self.getKit()
        currdir = kit.foldername

        dlg = wx.FileDialog(
            self, message="Choose a file", defaultDir=currdir, 
            defaultFile="", wildcard=wildcard, style=wx.OPEN | wx.CHANGE_DIR
            )

        # Show the dialog and retrieve the user response. If it is the OK response, 
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            # This returns a Python list of files that were selected.
            files = dlg.GetPaths()
            if len(files)>0:
                newfile = os.path.normcase(files[0])
                # make relative path
                self.SetStringSelection(makeRelativePath(newfile, kit.foldername))

                # add kit to modified set
                self.frame.addKitToModified(kit)


"""
A file choice with label
"""
class MyShortsNumPalFile(MyNumbersFile):

    def SetStringSelection(self, str=None):
        kit = self.getKit()
        if str == None:
            try: str = kit.attributes[self.att % kit.shortsKey]
            except KeyError: str = "undefined"
        self.text.SetValue(str)
        kit.attributes[self.att % kit.shortsKey] = str
        if self.refreshOnChange:
            self.frame.kitPanel.Refresh()

    def SetUndef(self):
        kit = self.getKit()
        self.text.SetValue("")
        try:
            del kit.attributes[self.att % kit.shortsKey] 
            del kit.attributes["shorts.num-pal"]
        except AttributeError:
            pass
        except KeyError:
            pass
        if self.refreshOnChange:
            self.frame.kitPanel.Refresh()

    def OnChooseFile(self, event):
        wildcard = "PNG images (*.png)|*.png|" \
                   "BMP images (*.bmp)|*.bmp"

        kit = self.getKit()
        currdir = kit.foldername

        dlg = wx.FileDialog(
            self, message="Choose a file", defaultDir=currdir, 
            defaultFile="", wildcard=wildcard, style=wx.OPEN | wx.CHANGE_DIR
            )

        # Show the dialog and retrieve the user response. If it is the OK response, 
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            # This returns a Python list of files that were selected.
            files = dlg.GetPaths()
            if len(files)>0:
                newfile = os.path.normcase(files[0])
                foldername = "%s\\%s" % (os.path.split(kit.foldername)[0], kit.shortsKey)
                # make relative path
                self.SetStringSelection(makeRelativePath(newfile, foldername))

                # add kit to modified set
                self.frame.addKitToModified()

        dlg.Destroy()


"""
A dir choice with label
"""
class MyPartFolder(MyNumbersFile):

    def __init__(self, parent, attribute, labelText, value, rootPath, frame, kit=None):
        wx.Panel.__init__(self, parent, -1)
        self.rootPath = rootPath
        self.frame = frame
        self.kit = kit
        self.att = attribute
        self.label = wx.StaticText(self, -1, labelText, size=(140,-1), style=wx.ALIGN_RIGHT)
        self.label.SetBackgroundColour(wx.Colour(230,230,230))
        font = wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.label.SetFont(font)
        self.label.SetSize(self.label.GetBestSize())

        self.text = wx.TextCtrl(self, -1, "", size=(130,-1))
        self.text.SetEditable(False)
        self.button = wx.Button(self, -1, "undef", size=(60,1))
        self.fileButton = wx.Button(self, -1, "...", size=(30,1))

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.button, 0, wx.RIGHT | wx.EXPAND, border=10)
        self.sizer.Add(self.label, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=10)
        self.sizer.Add(self.text, 0, wx.EXPAND)
        self.sizer.Add(self.fileButton, 0, wx.EXPAND)

        # by default the kit panel is not refreshed on selection change
        self.refreshOnChange = False

        # bind events
        #self.text.Bind(wx.EVT_CHOICE, self.OnSelect)
        self.button.Bind(wx.EVT_BUTTON, self.OnUndef)
        self.fileButton.Bind(wx.EVT_BUTTON, self.OnChooseFile)

        self.SetSizer(self.sizer)
        self.Layout()

    def SetStringSelection(self, str=None):
        kit = self.getKit()
        if str == None:
            try: str = kit.attributes[self.att]
            except KeyError: str = "undefined"
        self.text.SetValue(str)
        kit.attributes[self.att] = str
        if self.refreshOnChange:
            self.frame.kitPanel.Refresh()

    def SetUndef(self):
        kit = self.getKit()
        self.text.SetValue("")
        try:
            del kit.attributes[self.att] 
        except AttributeError:
            pass
        except KeyError:
            pass
        if self.refreshOnChange:
            self.frame.kitPanel.Refresh()

    def OnChooseFile(self, event):
        kit = self.getKit()
        tokens = os.path.split(kit.foldername)
        items = [d for d in os.listdir(tokens[0])
                    if os.path.isdir("%s/%s" % (tokens[0],d)) and d[0] in ['p','g']]
        defaultItem = kit.attributes.get(self.att)
        dlg = wx.SingleChoiceDialog(
                self, 'Select the kit part folder', 'Folder selector', items,
                wx.CHOICEDLG_STYLE
                )
        if defaultItem in items: dlg.SetSelection(items.index(defaultItem))
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetStringSelection()
            print "You selected: %s" % path
            if path:
                newpath = os.path.normcase(path)
                self.SetStringSelection(newpath)

                # add kit to modified set
                self.frame.addKitToModified()

        dlg.Destroy()

"""
A file choice with label
"""
class MyMaskFile(MyPartFolder):

    def SetStringSelection(self, str=None):
        kit = self.getKit()
        if not str: str = kit.attributes.get(self.att,"")
        self.text.SetValue(str)
        kit.attributes[self.att] = str
        if self.refreshOnChange:
            self.frame.kitPanel.Refresh()

    def SetUndef(self):
        kit = self.getKit()
        self.text.SetValue("")
        try:
            del kit.attributes[self.att]
        except AttributeError:
            pass
        except KeyError:
            pass
        if self.refreshOnChange:
            self.frame.kitPanel.Refresh()

    def OnChooseFile(self, event):
        wildcard = "PNG images (*.png)|*.png|" \
                   "BMP images (*.bmp)|*.bmp"

        kit = self.getKit()
        curvalue = kit.attributes.get(self.att)
        if not curvalue:
            defaultDir = self.frame.gdbPath + "/uni/masks"
        else:
            # check to see if the file exists relative to kit dir
            fullpath = "%s/%s" % (kit.foldername, curvalue)
            if os.path.exists(fullpath):
                defaultDir = os.path.split(fullpath)[0]
            else:
                fullpath = "%s/uni/masks/%s" % (self.frame.gdbPath, curvalue)
                if os.path.exists(fullpath):
                    defaultDir = os.path.split(fullpath)[0]
                else:
                    defaultDir = self.frame.gdbPath + "/uni/masks"

        defaultFile = kit.attributes.get(self.att,DEFAULT_MASK)

        dlg = wx.FileDialog(
            self, message="Choose a file", defaultDir=defaultDir, 
            defaultFile="", wildcard=wildcard, style=wx.OPEN | wx.CHANGE_DIR
            )

        # Show the dialog and retrieve the user response. If it is the OK response, 
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            # This returns a Python list of files that were selected.
            files = dlg.GetPaths()
            if len(files)>0:
                newfile = os.path.normcase(files[0])
                kitBasedir = os.path.normcase(kit.foldername)
                standardBasedir = os.path.normcase(self.frame.gdbPath + "/uni/masks")
                # make relative path
                relpath1 = makeRelativePath(newfile,kitBasedir)
                relpath2 = makeRelativePath(newfile,standardBasedir)
                if len(relpath1)<=len(relpath2):
                    self.SetStringSelection(relpath1)
                else:
                    self.SetStringSelection(relpath2)

                # add kit to modified set
                self.frame.addKitToModified(kit)

        dlg.Destroy()


"""
A file choice with label
"""
class MyOverlayFile(MyPartFolder):

    def SetStringSelection(self, str=None):
        kit = self.getKit()
        if not str: str = kit.attributes.get(self.att,"")
        self.text.SetValue(str)
        kit.attributes[self.att] = str
        if self.refreshOnChange:
            self.frame.kitPanel.Refresh()

    def SetUndef(self):
        kit = self.getKit()
        self.text.SetValue("")
        try:
            del kit.attributes[self.att]
        except AttributeError:
            pass
        except KeyError:
            pass
        if self.refreshOnChange:
            self.frame.kitPanel.Refresh()

    def OnChooseFile(self, event):
        wildcard = "PNG images (*.png)|*.png|" \
                   "BMP images (*.bmp)|*.bmp"

        kit = self.getKit()
        curvalue = kit.attributes.get(self.att)
        if not curvalue:
            defaultDir = self.frame.gdbPath + "/uni/overlay"
        else:
            # check to see if the file exists relative to kit dir
            fullpath = "%s/%s" % (kit.foldername, curvalue)
            if os.path.exists(fullpath):
                defaultDir = os.path.split(fullpath)[0]
            else:
                fullpath = "%s/uni/overlay/%s" % (self.frame.gdbPath, curvalue)
                if os.path.exists(fullpath):
                    defaultDir = os.path.split(fullpath)[0]
                else:
                    defaultDir = self.frame.gdbPath + "/uni/overlay"

        dlg = wx.FileDialog(
            self, message="Choose a file", defaultDir=defaultDir, 
            defaultFile="", wildcard=wildcard, style=wx.OPEN | wx.CHANGE_DIR
            )

        # Show the dialog and retrieve the user response. If it is the OK response, 
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            # This returns a Python list of files that were selected.
            files = dlg.GetPaths()
            if len(files)>0:
                newfile = os.path.normcase(files[0])
                kitBasedir = os.path.normcase(kit.foldername)
                standardBasedir = os.path.normcase(self.frame.gdbPath + "/uni/overlay")
                # make relative path
                relpath1 = makeRelativePath(newfile,kitBasedir)
                relpath2 = makeRelativePath(newfile,standardBasedir)
                if len(relpath1)<=len(relpath2):
                    self.SetStringSelection(relpath1)
                else:
                    self.SetStringSelection(relpath2)

                # add kit to modified set
                self.frame.addKitToModified(kit)

        dlg.Destroy()

"""
A panel with kit texture
"""
class KitPanel(wx.Panel):
    def __init__(self, parent, frame=None):
        wx.Panel.__init__(self, parent, -1, size=(512, 256))
        self.SetBackgroundColour(wx.Color(180,180,200))
        self.frame = frame
        self.kit = None

        # bind events
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def getPartFile(self, kit, part):
        partFolder = kit.attributes.get("%s.folder" % part)
        if partFolder: foldername = "%s/%s" % (os.path.split(kit.foldername)[0], partFolder)
        else: foldername = kit.foldername
        filename = "%s/%s.png" % (foldername,part)
        if os.path.exists(filename):
            return filename
        filename = "%s/%s.bmp" % (foldername,part)
        if os.path.exists(filename):
            return filename
        filename = "%s/all.png" % foldername
        if os.path.exists(filename):
            return filename
        filename = "%s/all.bmp" % foldername
        if os.path.exists(filename):
            return filename
        return None

    def getOverlayFile(self,kit,overlay):
        # check the team folder first
        filename = os.path.normcase("%s/%s" % (kit.foldername,overlay))
        if os.path.exists(filename): return filename
        # check the standard folder
        filename = os.path.normcase("%s/uni/overlay/%s" % (self.frame.gdbPath,overlay))
        if os.path.exists(filename): return filename
        # overlay file not found
        print >>sys.stderr,"overlay '%s' NOT found for kit: %s" % (overlay,kit.foldername)
        return None

    def getMaskFile(self,kit,mask):
        # check the team folder first
        filename = os.path.normcase("%s/%s" % (kit.foldername,mask))
        if os.path.exists(filename): return filename
        # check the standard folder
        filename = os.path.normcase("%s/uni/masks/%s" % (self.frame.gdbPath,mask))
        if os.path.exists(filename): return filename
        # mask file not found
        print >>sys.stderr,"mask file '%s' NOT found for kit: %s" % (mask,kit.foldername)
        return None


    def drawFiles(self, dc, kit, files):
        drawnSome = False
        for part,file in files:
            if file:
                bmp = wx.Bitmap(file)
                width,height = bmp.GetSize()
                if part=="shirt":
                    self.frame.SetTitle("%s: (%dx%d) kit" % (WINDOW_TITLE,width,height))
                if width != 512 or height != 256:
                    bmp = bmp.ConvertToImage().Scale(512,256).ConvertToBitmap()

                img = bmp.ConvertToImage()
                maskfile = self.getMaskFile(kit, self.kit.attributes.get("mask",DEFAULT_MASK))
                if maskfile and len(files)>1:
                    maskImg = wx.Bitmap(maskfile).ConvertToImage()
                    applyColourMask(img, maskImg, MASK_COLORS[part])
                dc.DrawBitmap(img.ConvertToBitmap(),0,0,True)
                drawnSome = True
        overlay = kit.attributes.get("overlay")
        if overlay:
            overlayfile = self.getOverlayFile(kit,overlay)
            if overlayfile:
                bmp = wx.Bitmap(overlayfile)
                img = bmp.ConvertToImage()
                width,height = bmp.GetSize()
                if width != 512 or height != 256:
                    img = img.Scale(512,256)
                if not img.HasAlpha() and not img.HasMask():
                    img.SetMaskColour(0xff,0,0xff) # pink overlay mask color
                dc.DrawBitmap(img.ConvertToBitmap(),0,0,True)
        return drawnSome

    def drawKit(self, dc, kit):
        files = [(part,self.getPartFile(kit,part)) for part in ["shirt","shorts","socks"]]
        if files[0][1]==files[1][1] and files[1][1]==files[2][1]: del files[1:]
        hasSomething = self.drawFiles(dc, kit, files)
        if not hasSomething:
            bmp = wx.Bitmap(DEFAULT_PNG)
            dc.DrawBitmap(bmp, 0, 0, True)

    def OnPaint(self, event):
        try: self.repaint(event)
        except Exception,info:
            print >>sys.stderr,info

    def repaint(self, event):
        dc = wx.PaintDC(self)

        # disable warning pop-ups
        wx.Log.EnableLogging(False)

        # draw kit
        if self.kit == None or self.kit.teamId == -1:
            self.frame.SetTitle(WINDOW_TITLE)
            bmp = wx.Bitmap(DEFAULT_PNG)
            dc.DrawBitmap(bmp, 0, 0, True)
            return event.Skip()
        else:
            self.drawKit(dc, self.kit)

        # draw some overlay items
        kit = self.kit
        p = overlayPositions

        plRect = wx.Rect(32*4,64,32,64)
        gkRect = wx.Rect(32*1,0,32,64)
        if os.path.split(kit.foldername)[1][0] == 'g':
            rect = gkRect
        else:
            rect = plRect

        # determine shirt type
        try: 
            stp = getKitTemplateType(kit.attributes["model"])
        except KeyError:
            stp = "pes6-new"

        kitKey = os.path.split(kit.foldername)[1]
        if os.path.exists(kit.foldername + "/config.txt"):
            readAttributes(kit)

        # render number
        try: numbers = "%s/%s" % (kit.foldername, kit.attributes["numbers"])
        except KeyError: numbers = ""
        if os.path.exists(numbers):
            bmp = wx.Bitmap(numbers).GetSubBitmap(rect)
            if p[stp]["num-height"] != 64:
                scaledbmp = bmp.ConvertToImage().Scale(32,p[stp]["num-height"]).ConvertToBitmap()
                dc.DrawBitmap(scaledbmp, p[stp]["numbers"][0], p[stp]["numbers"][1], True)
            else:
                dc.DrawBitmap(bmp, p[stp]["numbers"][0], p[stp]["numbers"][1], True)

            # render number on the chest, if this is a national kit
            if isNationalKit(self.kit.teamId):
                snl = kit.attributes.get("shirt.number.location","center")
                if snl != "undefined" and snl != "off":
                    scaledbmp = bmp.ConvertToImage().Scale(16,p[stp]["chest-num-height"]).ConvertToBitmap()
                    dc.DrawBitmap(scaledbmp, p[stp]["chest-%s" % snl][0], p[stp]["chest-%s" % snl][1], True)

            # render number on shorts, using palette file
            try: numpal = "%s/%s" % (kit.foldername, kit.attributes["shorts.num-pal."+kit.shortsKey])
            except KeyError:
                try: numpal = "%s/%s" % (kit.foldername, kit.attributes["shorts.num-pal"])
                except KeyError: numpal = ""
            if os.path.exists(numpal):
                try: shortsLoc = self.frame.shortsNumLocation.kit.attributes["shorts.number.location"]
                except KeyError: shortsLoc = "left"

                if shortsLoc == "left" or shortsLoc == "both":
                    bmp = getBitmapWithPalette(numbers,numpal,rect)
                    scaledbmp = bmp.ConvertToImage().Scale(16,p[stp]["shorts-num-height"]).ConvertToBitmap()
                    dc.DrawBitmap(scaledbmp, p[stp]["shorts-left"][0], p[stp]["shorts-left"][1], True)
                if shortsLoc == "right" or shortsLoc == "both":
                    bmp = getBitmapWithPalette(numbers,numpal,rect)
                    scaledbmp = bmp.ConvertToImage().Scale(16,p[stp]["shorts-num-height"]).ConvertToBitmap()
                    dc.DrawBitmap(scaledbmp, p[stp]["shorts-right"][0], p[stp]["shorts-right"][1], True)

        # render name
        font = "%s/%s" % (kit.foldername, "font.png")
        if not os.path.exists(font):
            font = "%s/%s" % (kit.foldername, "font.bmp")
        if os.path.exists(font):
            try: type = kit.attributes["name.shape"]
            except KeyError: type = "type1"
            try: pos = kit.attributes["name.location"]
            except KeyError: pos = "top"

            if pos == "top" or pos == "bottom":
                rect1 = wx.Rect(0,0,20,32)
                rect2 = wx.Rect(20,0,20,32)
                rect3 = wx.Rect(40,0,20,32)
                bmp = wx.Bitmap(font).GetSubBitmap(rect1)
                img = bmp.ConvertToImage().Scale(20,p[stp]["font-height"])
                if pos == "top":
                    if type == "type2": img = img.Rotate(math.pi/12,wx.Point(19,31))
                    elif type == "type3": img = img.Rotate(math.pi/6,wx.Point(19,31))
                bmp = img.ConvertToBitmap()
                dc.DrawBitmap(bmp, p[stp]["nameA-%s-%s" % (type,pos)][0], p[stp]["nameA-%s-%s" % (type,pos)][1], True)
                bmp = wx.Bitmap(font).GetSubBitmap(rect2)
                bmp = bmp.ConvertToImage().Scale(20,p[stp]["font-height"]).ConvertToBitmap()
                dc.DrawBitmap(bmp, p[stp]["nameB-%s-%s" % (type,pos)][0], p[stp]["nameB-%s-%s" % (type,pos)][1], True)
                bmp = wx.Bitmap(font).GetSubBitmap(rect3)
                img = bmp.ConvertToImage().Scale(20,p[stp]["font-height"])
                if pos == "top":
                    if type == "type2": img = img.Rotate(-math.pi/12,wx.Point(0,31))
                    elif type == "type3": img = img.Rotate(-math.pi/6,wx.Point(0,31))
                bmp = img.ConvertToBitmap()
                dc.DrawBitmap(bmp, p[stp]["nameC-%s-%s" % (type,pos)][0], p[stp]["nameC-%s-%s" % (type,pos)][1], True)

        # re-enable warning pop-ups
        wx.Log.EnableLogging(True)

        nameText, numberText = "ABC", "9"
        if self.kit.isKeeper:
            numberText = "1"

        # shirt name
        try:
            colorName = MakeRGBAColor(self.kit.attributes["shirt.name"])
            if colorName.alpha != 0:
                dc.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD, False))
                dc.SetTextForeground(colorName.color)
                try:
                    if self.kit.attributes["name.shape"] == "curved":
                        dc.DrawRotatedText(nameText[0], 238, 15, 7)
                        dc.DrawText(nameText[1], 253, 15)
                        dc.DrawRotatedText(nameText[2], 268, 15, -7)
                    else:
                        dc.DrawText(nameText, 238, 15)
                except KeyError:
                    dc.DrawText(nameText, 238, 15)
        except KeyError:
            pass

        # shirt number
        try:
            colorNumber = MakeRGBAColor(self.kit.attributes["shirt.number"])
            if colorNumber.alpha != 0:
                dc.SetFont(wx.Font(42, wx.SWISS, wx.NORMAL, wx.BOLD, False))
                dc.SetTextForeground(colorNumber.color)
                dc.DrawText(numberText, 244, 46)
        except KeyError:
            pass

        # shirt front number (for national teams)
        if self.kit.teamId < 64:
            try:
                colorNumber = MakeRGBAColor(self.kit.attributes["shirt.number"])
                if colorNumber.alpha != 0:
                    dc.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.BOLD, False))
                    dc.SetTextForeground(colorNumber.color)
                    dc.DrawText(numberText, 109, 66)
            except KeyError:
                pass

        # shorts number(s)
        try:
            colorShorts = MakeRGBAColor(self.kit.attributes["shorts.number"])
            if colorShorts.alpha != 0:
                dc.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.BOLD, False))
                dc.SetTextForeground(colorShorts.color)
                try:
                    shortsNumPos = self.kit.attributes["shorts.number.location"];
                    if shortsNumPos == "off":
                        positions = []
                    elif shortsNumPos == "right":
                        positions = [(40,205)]
                    elif shortsNumPos == "both":
                        positions = [(40,205), (120,205)]
                    else:
                        positions = [(120,205)]
                except KeyError:
                    positions = [(120,205)]
                for pos in positions:
                    dc.DrawText(numberText, pos[0], pos[1])
        except KeyError:
            pass


class Kit:
    def __init__(self, foldername):
        # create a kit with undefined attributes 
        self.foldername = os.path.normcase(foldername)
        self.attributes = dict()
        self.isKeeper = False # flag to indicate a GK kit
        self.attribRead = False # flag to indicate that attributes were already read
        self.teamId = -1


class GDBTree(wx.TreeCtrl):
    def __init__(self, parent, style, frame, gdbPath=""):
        wx.TreeCtrl.__init__(self, parent, -1, style=style)
        self.gdbPath = gdbPath
        self.frame = frame

        self.root = self.AddRoot("GDB")
        self.SetPyData(self.root, None)

        self.teamMap = dict()
        self.reverseTeamMap = dict()

        # bind events
        self.Bind(wx.EVT_TREE_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged)


    """
    Shows a warning window, with a choice of saving changes,
    discarding them, or cancelling the operation.
    """
    def cancelledOnSaveChanges(self):
        if len(self.frame.modified) > 0:
            # figure out what to do with changes: Save or Discard
            dlg = wx.MessageDialog(self, """You haven't saved your changes.
Do you want to save them?""",
                    "Save or Discard changes",
                    wx.YES_NO | wx.CANCEL | wx.ICON_INFORMATION)
            retValue = dlg.ShowModal()
            dlg.Destroy()

            if retValue == wx.ID_YES:
                # save the changes first
                self.frame.saveChanges(False)
                pass
            elif retValue == wx.ID_CANCEL:
                # cancel the operation
                return True

        self.frame.modified.clear()
        self.frame.SetStatusText("Modified kits: 0")
        return False

    
    def OnRefresh(self, event):
        if self.cancelledOnSaveChanges():
            return

        self.updateTree()
        self.frame.modified.clear()
        self.frame.SetStatusText("Modified kits: 0");
        self.frame.selectKit(None)
        print "GDB-tree updated."


    def OnKeyDown(self, event):
        key = event.GetKeyCode()
        item = self.GetSelection()
        if key == wx.WXK_RETURN:
            if self.IsExpanded(item):
                self.Collapse(item)
            else:
                self.Expand(item)


    def OnSelChanged(self, event):
        try:
            item = event.GetItem()
            print "OnSelChanged: %s" % self.GetItemText(item)
            kit = self.GetPyData(item)
            self.frame.selectKit(kit)

        except wx._core.PyAssertionError:
            pass

    """
    Creates new Kit object
    """
    def makeKit(self, path):
        kit = Kit(path)
        try: 
            foldername = os.path.normcase(os.path.split(path)[0])
            kit.teamId = self.reverseTeamMap[foldername]
            kit.shortsKey = os.path.split(path)[1]
        except KeyError: kit.teamId = -1
        return kit

    """
    Recursivelly adds specified path.
    """
    def addDir(self, node, path, inmap=False, cinmap=False):
        if os.path.isdir(path):
            child = self.AppendItem(node, "%s" % os.path.split(path)[1])
            kit = self.makeKit(path)
            self.SetPyData(child, kit)
            self.SetItemImage(child, self.fldridx, wx.TreeItemIcon_Normal)
            self.SetItemImage(child, self.fldropenidx, wx.TreeItemIcon_Expanded)

            inmap = inmap or self.reverseTeamMap.has_key(os.path.normcase(path))

            dirs = ["%s/%s" % (path,item) for item in os.listdir(path)]
            dirs.sort()
            for dir in dirs:
                cinmap = self.addDir(child,dir,inmap) or cinmap

            if not inmap and not cinmap:
                self.Delete(child)

            return cinmap or inmap


    def updateTree(self):
        self.CollapseAndReset(self.root)

        gdbPath = self.gdbPath

        isz = (16,16)
        il = wx.ImageList(isz[0], isz[1])
        self.fldridx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, isz))
        self.fldropenidx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN,   wx.ART_OTHER, isz))
        self.fileidx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, isz))

        self.SetImageList(il)
        self.il = il

        self.SetItemImage(self.root, self.fldridx, wx.TreeItemIcon_Normal)
        self.SetItemImage(self.root, self.fldropenidx, wx.TreeItemIcon_Expanded)

        # Populate the tree control with content from GDB.
        # The idea here is to only add those files/folders to the tree, which
        # actually are recognized and processed by Kitserver, and leave everything
        # else out of the tree control. (One exception to this rule is: config.txt
        # file in each team folder. Kitserver does process it, but we are not gonna
        # show that file in the tree.)

        try: 
            # read map.txt
            self.teamMap.clear()
            self.reverseTeamMap.clear()
            try: map = open(gdbPath + "/uni/map.txt","rt")
            except IOError: pass
            else:
                for line in map:
                    # strip off comments
                    comm = line.find("#")
                    if comm > -1:
                        line = line[:comm]

                    # strip off any remaining white space
                    line = line.strip()

                    tok = line.split(',',1)
                    if len(tok)==2:
                        id, val = int(tok[0].strip()), tok[1].strip()
                        if val[0]=='"' and val[-1]=='"': val = val[1:-1]
                        folder = os.path.normcase(self.gdbPath + "/uni/" + val)
                        self.teamMap[id] = folder
                        self.reverseTeamMap[folder] = id

                map.close()

            # add all the dirs
            teamDirs = self.addDir(self.root, gdbPath + "/uni")
        except IndexError, ex:
            dlg = wx.MessageDialog(self, """PROBLEM: GDB Manager is unable to read the
contents of your GDB. You selected: 

%s

Perhaps, you accidently selected a wrong folder. 
Please try choosing a different one.""" % self.gdbPath,
                    "GDB Manager ERROR",
                    wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()

            # trigger folder selection
            self.frame.OnSetFolder(None)

        # show the contents of GDB
        self.Expand(self.root)
        self.SetFocus()
        self.SelectItem(self.root)


class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(FRAME_WIDTH, FRAME_HEIGHT))
        self.gdbPath = "C:\\"
        self.kservCfgPath = ""

        # create a dictionary to keep track of modified kits
        self.modified = {}

        # status bar
        self.CreateStatusBar()
        self.SetStatusText("Modified kits: 0")

        # Create widgets
        ##################

        splitter = wx.SplitterWindow(self, -1, style=wx.SP_3D)

        # right parent panel
        p2 = wx.Panel(splitter, -1)

        # current kit panel
        self.kitPanel = KitPanel(p2, self)

        # model choice
        modellist = ["undefined"]
        for id in range(200):
            modellist.append(id)
        self.model = MyList(p2, "model", "3D-model ID:", modellist, self)
        self.model.refreshOnChange = True

        # collar choice
        self.collar = MyList(p2, "collar", "Collar:", ["undefined", "yes", "no"], self)

        # name-shape choice
        self.nameShape = MyList(p2, "name.shape", "Name shape:", ["undefined", "type1", "type2", "type3"], self)
        self.nameShape.refreshOnChange = True

        # name-location choice
        self.nameLocation = MyList(p2, "name.location", "Name location:", ["undefined", "off", "top", "bottom"], self)
        self.nameLocation.refreshOnChange = True

        # logo-location choice
        self.logoLocation = MyList(p2, "logo.location", "Logo location:", ["undefined", "off", "top", "bottom"], self)

        # numbers choice
        self.numbers = MyNumbersFile(p2, "numbers", "Numbers:", "undefined", self.gdbPath, self)
        self.numbers.refreshOnChange = True

        # palette choice
        self.numpal = MyShortsNumPalFile(p2, "shorts.num-pal.%s", "Palette:", "undefined", self.gdbPath, self)
        self.numpal.refreshOnChange = True

        # shirt-num-location choice
        self.shirtNumLocation = MyList(p2, "shirt.number.location", "Shirt front number location:", ["undefined", "off", "center", "topright"], self)
        self.shirtNumLocation.refreshOnChange = True

        # shorts-num-location choice
        self.shortsNumLocation = MyList(p2, "shorts.number.location", "Shorts number location:", ["undefined", "off", "left", "right", "both"], self)
        self.shortsNumLocation.refreshOnChange = True

        #self.checkShortsCombos = wx.Button(p2, -1, "Check other shorts combinations");
        #self.shortsKeys = MyKeyList(p2, "With shorts from", [], self);

        # radar color
        self.radarCS = KitColourSelect(p2, "radar.color", "Radar color:", self)

        # shorts color
        self.shortsCS = KitColourSelect(p2, "shorts.color", "Shorts color:", self)

        # kit decription
        self.desc = MyTextField(p2, "description", "Description:", "undefined", self.gdbPath, self)
        self.desc.refreshOnChange = True

        # shirt.folder choice
        self.shirtFolder = MyPartFolder(p2, "shirt.folder", "Shirt Folder:", "undefined", self.gdbPath, self)
        self.shirtFolder.refreshOnChange = True

        # shorts.folder choice
        self.shortsFolder = MyPartFolder(p2, "shorts.folder", "Shorts Folder:", "undefined", self.gdbPath, self)
        self.shortsFolder.refreshOnChange = True

        # shorts.folder choice
        self.socksFolder = MyPartFolder(p2, "socks.folder", "Socks Folder:", "undefined", self.gdbPath, self)
        self.socksFolder.refreshOnChange = True

        # mask file choice
        self.maskFile = MyMaskFile(p2, "mask", "Mask:", "undefined", self.gdbPath, self)
        self.maskFile.refreshOnChange = True

        # overlay file choice
        self.overlayFile = MyOverlayFile(p2, "overlay", "Overlay:", "undefined", self.gdbPath, self)
        self.overlayFile.refreshOnChange = True

        # Kit database folder
        try:
            cfg = open(CONFIG_FILE, "rt")
            self.gdbPath = cfg.readline().strip()
            print "self.gdbPath = {%s}" % self.gdbPath
            self.kservCfgPath = cfg.readline().strip()
            print "self.kservCfgPath = {%s}" % self.kservCfgPath
            cfg.close()
            self.populateMiniKitLists()
        except IOError:
            self.OnSetFolder(None)

        # tree control
        self.tree = GDBTree(splitter, wx.TR_HAS_BUTTONS, self, self.gdbPath)
        self.tree.updateTree()

        # menu
        menubar = wx.MenuBar()

        menu1 = wx.Menu()
        menu1.Append(101, "&GDB folder", 
            "Set/change the location of GDB folder. Your current is: %s" % self.gdbPath)
        menu1.Append(102, "&Save changes", "Save the changes to attrib.cfg files")
        menu1.AppendSeparator()
        menu1.Append(103, "E&xit", "Exit the program")
        menubar.Append(menu1, "&File")

        menu2 = wx.Menu()
        menu2.Append(202, "&Restore this kit", "Undo changes for this kit")
        menu2.Append(201, "Re&fresh GDB", "Reload the GDB from disk")
        menubar.Append(menu2, "&Edit")

        menu4 = wx.Menu()
        menu4.Append(401, "&Link to kserv.cfg", "Link to mini-kits list defined in kserv.cfg")
        menubar.Append(menu4, "&Tools")

        menu3 = wx.Menu()
        menu3.Append(301, "&About", "Author and version information")
        menubar.Append(menu3, "&Help")

        self.SetMenuBar(menubar)

        # Create sizers
        #################

        self.rightSizer = wx.BoxSizer(wx.VERTICAL)
        p2.SetSizer(self.rightSizer)

        # Build interface by adding widgets to sizers
        ################################################

        self.rightSizer.Add(self.kitPanel, 0, wx.BOTTOM | wx.ALIGN_CENTER, border=10)
        self.rightSizer.Add(self.model, 0, wx.LEFT | wx.ALIGN_CENTER, border=10)
        self.rightSizer.Add(self.collar, 0, wx.LEFT | wx.ALIGN_CENTER, border=10)
        self.rightSizer.Add(self.nameShape, 0, wx.LEFT | wx.ALIGN_CENTER, border=10)
        self.rightSizer.Add(self.nameLocation, 0, wx.LEFT | wx.ALIGN_CENTER, border=10)
        self.rightSizer.Add(self.logoLocation, 0, wx.LEFT | wx.ALIGN_CENTER, border=10)
        self.rightSizer.Add(self.numbers, 0, wx.LEFT | wx.ALIGN_CENTER, border=10)
        self.rightSizer.Add(self.shirtNumLocation, 0, wx.LEFT | wx.BOTTOM | wx.ALIGN_CENTER, border=10)
        self.rightSizer.Add(self.shortsNumLocation, 0, wx.LEFT | wx.TOP | wx.ALIGN_CENTER, border=10)
        self.rightSizer.Add(self.numpal, 0, wx.LEFT | wx.ALIGN_CENTER, border=10)
        #self.rightSizer.Add(self.checkShortsCombos, 0, wx.LEFT | wx.BOTTOM | wx.ALIGN_CENTER, border=10)
        #self.rightSizer.Add(self.shortsKeys, 0, wx.LEFT | wx.BOTTOM | wx.ALIGN_CENTER, border=10)
        self.rightSizer.Add(self.radarCS, 0, wx.LEFT | wx.ALIGN_CENTER, border=10)
        self.rightSizer.Add(self.shortsCS, 0, wx.LEFT | wx.ALIGN_CENTER, border=10)
        self.rightSizer.Add(self.desc, 0, wx.LEFT | wx.BOTTOM | wx.ALIGN_CENTER, border=10)
        self.rightSizer.Add(self.shirtFolder, 0, wx.LEFT | wx.TOP | wx.ALIGN_CENTER, border=10)
        self.rightSizer.Add(self.shortsFolder, 0, wx.LEFT | wx.ALIGN_CENTER, border=10)
        self.rightSizer.Add(self.socksFolder, 0, wx.LEFT | wx.ALIGN_CENTER, border=10)
        self.rightSizer.Add(self.maskFile, 0, wx.LEFT | wx.ALIGN_CENTER, border=10)
        self.rightSizer.Add(self.overlayFile, 0, wx.LEFT | wx.ALIGN_CENTER, border=10)

        splitter.SetMinimumPaneSize(80)
        splitter.SplitVertically(self.tree, p2, -520)

        #self.Layout()

        # Bind events
        self.Bind(wx.EVT_CLOSE, self.OnExit)

        self.Bind(wx.EVT_MENU, self.OnSetFolder, id=101)
        self.Bind(wx.EVT_MENU, self.OnMenuSave, id=102)
        self.Bind(wx.EVT_MENU, self.OnExit, id=103)
        self.Bind(wx.EVT_MENU, self.OnRestore, id=202)
        self.Bind(wx.EVT_MENU, self.tree.OnRefresh, id=201)
        self.Bind(wx.EVT_MENU, self.OnSetKservCfg, id=401)
        self.Bind(wx.EVT_MENU, self.OnAbout, id=301)

        #self.checkShortsCombos.Bind(wx.EVT_BUTTON, self.OnCheckShortsCombos)

    def populateMiniKitLists(self):
        global narrowBacks, wideBacks, squashedWithLogo
        try:
            kservCfg = open(self.kservCfgPath, "rt")
            for line in kservCfg:
                # strip out the comment
                commentStarts = line.find("#")
                if commentStarts != -1:
                    line = line[:commentStarts]

                if len(line.strip())==0:
                    continue

                # look for lists
                toks = re.findall("([-\w.]+)\s?=\s?\[([^\]]*)\]",line)
                if len(toks)>0 and len(toks[0]) == 2:
                    if toks[0][0]=="mini-kits.narrow-backs":
                        narrowBacks = [int(v) for v in toks[0][1].split(',')]
                    elif toks[0][0]=="mini-kits.wide-backs":
                        wideBacks = [int(v) for v in toks[0][1].split(',')]
                    elif toks[0][0]=="mini-kits.squashed-with-logo":
                        squashedWithLogo = [int(v) for v in toks[0][1].split(',')]
        except IOError:
            print "Unable to read kserv.cfg"

        print "Mini-kit lists:"
        print "narrowBacks = %s" % narrowBacks
        print "wideBacks = %s" % wideBacks
        print "squashedWithLogo = %s" % squashedWithLogo


    """
    Shows dialog window to select the GDB folder.
    """
    def OnSetFolder(self, event):
        try:
            if self.tree.cancelledOnSaveChanges():
                return
        except AttributeError:
            # no tree yet. ignore then
            pass

        print "Set/change GDB folder location"
        dlg = wx.DirDialog(self, """Select your GDB folder:
(Folder named "GDB", which is typically located
inside your kitserver folder)""",
                style=wx.DD_DEFAULT_STYLE)

        if dlg.ShowModal() == wx.ID_OK:
            self.gdbPath = dlg.GetPath()
            print "You selected %s" % self.gdbPath

            # clear out kit panel, and disable controls
            self.enableControls(None)
            self.kitPanel.kit = None
            self.kitPanel.Refresh()

            # try to update the tree
            try:
                self.tree.gdbPath = self.gdbPath
                self.tree.updateTree()
            except AttributeError:
                # looks like we don't have a tree yet. 
                # so just rememeber this value for now.
                pass

            # save the value in configuration file
            print "Saving configuration into gdbm.cfg..."
            try:
                cfg = open(CONFIG_FILE, "wt")
                print >>cfg, self.gdbPath
                print "self.gdbPath = {%s}" % self.gdbPath
                print >>cfg, self.kservCfgPath
                print "self.kservCfgPath = {%s}" % self.kservCfgPath
                cfg.close()
            except IOError:
                # unable to save configuration file
                print "Unable to save configuration file"

        else:
            print "Selection cancelled."

        # destroy the dialog after we're done
        dlg.Destroy()


    def selectKit(self, kit):
        self.enableControls(kit)

        if kit != None:
            readAttributes(kit)
        else:
            self.SetTitle(WINDOW_TITLE)

        # assign this kit to kitPanel
        self.kitPanel.kit = kit
        self.kitPanel.Refresh()

        # update collar
        try:
            self.collar.SetStringSelection(kit.attributes["collar"])
        except:
            self.collar.SetUndef()

        # update model
        try:
            self.model.SetStringSelection(kit.attributes["model"])
        except:
            self.model.SetUndef()

        # update nameShape
        try:
            self.nameShape.SetStringSelection(kit.attributes["name.shape"])
        except:
            self.nameShape.SetUndef()

        # update nameLocation
        try:
            self.nameLocation.SetStringSelection(kit.attributes["name.location"])
        except:
            self.nameLocation.SetUndef()

        # update logoLocation
        try:
            self.logoLocation.SetStringSelection(kit.attributes["logo.location"])
        except:
            self.logoLocation.SetUndef()

        # update shirtNumLocation
        try:
            self.shirtNumLocation.kit = kit
            self.shirtNumLocation.SetStringSelection(kit.attributes["shirt.number.location"])
        except:
            self.shirtNumLocation.SetUndef()

        # update shortsNumLocation
        #try:
        #    self.shortsNumLocation.SetStringSelection(kit.attributes["shorts.number.location"])
        #except:
        #    self.shortsNumLocation.SetUndef()
        try:
            self.shortsNumLocation.kit = kit
            self.shortsNumLocation.SetStringSelection(kit.attributes["shorts.number.location"])
        except:
            self.shortsNumLocation.SetUndef()

        # update numbers
        try:
            self.numbers.SetStringSelection(kit.attributes["numbers"])
        except:
            self.numbers.SetUndef()

        # update numpal
        try:
            self.numpal.SetStringSelection(kit.attributes["shorts.num-pal.%s" % kit.shortsKey])
        except:
            try: self.numpal.SetStringSelection(kit.attributes["shorts.num-pal"])
            except: 
                self.numpal.SetUndef()

        # update radar color
        try:
            self.radarCS.SetRGBAColour(MakeRGBAColor(kit.attributes["radar.color"]))
        except:
            self.radarCS.ClearColour()

        # update folder
        try:
            self.shirtFolder.SetStringSelection(kit.attributes["shirt.folder"])
        except:
            self.shirtFolder.SetUndef()

        # update folder
        try:
            self.shortsFolder.SetStringSelection(kit.attributes["shorts.folder"])
        except:
            self.shortsFolder.SetUndef()

        # update folder
        try:
            self.socksFolder.SetStringSelection(kit.attributes["socks.folder"])
        except:
            self.socksFolder.SetUndef()

        # mask file
        try:
            self.maskFile.SetStringSelection(kit.attributes["mask"])
        except:
            self.maskFile.SetUndef()

        # mask file
        try:
            self.overlayFile.SetStringSelection(kit.attributes["overlay"])
        except:
            self.overlayFile.SetUndef()

        # update shorts color
        try:
            self.shortsCS.SetRGBAColour(MakeRGBAColor(kit.attributes["shorts.color"]))
        except:
            self.shortsCS.ClearColour()

        # update description
        try:
            self.desc.SetStringSelection(kit.attributes["description"])
        except:
            self.desc.SetUndef()

        # hide True key, show "Check shorts combinations" button
        #for x in range(self.shortsKeys.choice.GetCount()):
        #    self.shortsKeys.choice.Delete(0)
        #self.shortsKeys.Enable(False)
        if kit != None and kit.teamId != -1:
            #self.checkShortsCombos.Enable(True)
            # reset shorts-key
            kit.shortsKey = os.path.split(kit.foldername)[1]


    def enableControls(self, kit):
        if kit == None or kit.teamId == -1:
            self.collar.Enable(False)
            self.model.Enable(False)
            self.nameShape.Enable(False)
            self.shirtNumLocation.Enable(False)
            self.shortsNumLocation.Enable(False)
            self.nameLocation.Enable(False)
            self.logoLocation.Enable(False)
            self.logoLocation.Enable(False)
            self.numpal.Enable(False)
            self.numbers.Enable(False)
            #self.shortsKeys.Enable(False)
            #self.checkShortsCombos.Enable(False)
            self.radarCS.Enable(False)
            self.shortsCS.Enable(False)
            self.desc.Enable(False)
            self.shirtFolder.Enable(False)
            self.shortsFolder.Enable(False)
            self.socksFolder.Enable(False)
            self.maskFile.Enable(False)
            self.overlayFile.Enable(False)
        else:
            self.collar.Enable(True)
            self.model.Enable(True)
            self.nameShape.Enable(True)
            self.shirtNumLocation.Enable(True)
            self.shortsNumLocation.Enable(True)
            self.nameLocation.Enable(True)
            self.logoLocation.Enable(True)
            self.numpal.Enable(True)
            self.numbers.Enable(True)
            #self.shortsKeys.Enable(False)
            #self.checkShortsCombos.Enable(True)
            self.radarCS.Enable(True)
            self.shirtFolder.Enable(True)
            self.shortsFolder.Enable(True)
            self.socksFolder.Enable(True)
            self.maskFile.Enable(True)
            self.overlayFile.Enable(True)
            self.shortsCS.Enable(True)
            self.desc.Enable(True)


    def OnRestore(self, event):
        if self.kitPanel.kit == None:
            return

        self.kitPanel.kit.attribRead = False
        self.selectKit(self.kitPanel.kit)

        # remove kit from list of modified kits
        self.removeKitFromModified()

    """
    Checks if any other shorts for this team have the
    same palette as the shirt from current kit.
    """
    def OnCheckShortsCombos(self, event):
        self.checkShortsCombos.Enable(False)
        teamFolder, kitKey = os.path.split(self.kitPanel.kit.foldername)
        for x in range(self.shortsKeys.choice.GetCount()):
            self.shortsKeys.choice.Delete(0)

        # find all shorts with the same palette
        parent = self.tree.GetItemParent(self.tree.GetSelection())
        allkits = []
        child,cookie = self.tree.GetFirstChild(parent)
        if (child): allkits.append(self.tree.GetItemPyData(child))
        while child:
            child,cookie = self.tree.GetNextChild(parent,cookie)
            if (child): allkits.append(self.tree.GetItemPyData(child))
        kitKeyList = []
        for kit in allkits:
            if hasSamePalette(self.kitPanel.kit.foldername, kit.foldername):
                readAttributes(kit)
                item = os.path.split(kit.foldername)[1]
                self.shortsKeys.choice.Append(item, kit)
                kitKeyList.append(item)

        if len(kitKeyList) > 0:
            # pre-select current kit
            self.shortsKeys.choice.SetSelection(0)
            self.kitPanel.kit.shortsKey = kitKeyList[0]
            for item,i in zip(kitKeyList,range(len(kitKeyList))):
                if item == kitKey:
                    self.shortsKeys.choice.SetSelection(i)
                    self.kitPanel.kit.shortsKey = item
                    break

        self.shortsKeys.Enable(True)
        self.kitPanel.Refresh()

    def addKitToModified(self, kit=None):
        if kit != None:
            self.modified[kit] = True
        else:
            self.modified[self.kitPanel.kit] = True
        # update status bar text
        self.SetStatusText("Modified kits: %d" % len(self.modified.keys()))


    def removeKitFromModified(self):
        try:
            del self.modified[self.kitPanel.kit]
            # update status bar text
            self.SetStatusText("Modified kits: %d" % len(self.modified.keys()))
        except KeyError:
            pass
            

    def OnMenuSave(self, event):
        self.saveChanges()
        self.modified.clear()
        self.SetStatusText("Modified kits: 0");
        print "Changes saved."


    def OnSetKservCfg(self, event):
        print "Linking to kserv.cfg"
        dlg = wx.FileDialog(self, """Navigate to your kserv.cfg file and select it.""",
                defaultDir=os.getcwd(),
                style=wx.DD_DEFAULT_STYLE)
        dlg.SetWildcard("kserv.cfg files|kserv.cfg");

        if dlg.ShowModal() == wx.ID_OK:
            self.kservCfgPath = dlg.GetPath()
            print "You selected %s" % self.kservCfgPath

            # save the value in configuration file
            print "Saving configuration into gdbm.cfg..."
            try:
                cfg = open(CONFIG_FILE, "wt")
                print >>cfg, self.gdbPath
                print "self.gdbPath = {%s}" % self.gdbPath
                print >>cfg, self.kservCfgPath
                print "self.kservCfgPath = {%s}" % self.kservCfgPath
                cfg.close()
                self.populateMiniKitLists()
            except IOError:
                # unable to save configuration file
                print "Unable to save configuration file"
        else:
            print "Selection cancelled."

        # destroy the dialog after we're done
        dlg.Destroy()

    def OnAbout(self, event):
        dlg = wx.MessageDialog(self, """GDB Manager by Juce.
Version %s from %s

This is a helper program for working with GDB (Graphics Database)
for Kitserver 6. Provides simple visual interface to
define different attributes for kits: 3D-model, collar, image
files for names and numbers, and some others.""" % (VERSION, DATE),
            "About GDB Manager", wx.OK | wx.ICON_INFORMATION)

        dlg.ShowModal()
        dlg.Destroy()


    def OnExit(self, evt):
        print "MyFrame.OnExit"

        # do necessary clean-up and saves
        if self.tree.cancelledOnSaveChanges():
            return

        # Exit the program
        self.Destroy()
        sys.exit(0)


    """
    Saves the changes for altered kits to corresponding attrib.cfg files
    """
    def saveChanges(self, showConfirmation=True):
        print "Saving changes..."

        # TEMP:test
        print "Modified kits [%d]:" % len(self.modified.keys())
        for kit in self.modified.keys():
            # for now: just print out the kit foldername
            print kit.foldername

        # write config.txt for each modified kit
        for kit in self.modified.keys():
            att = None

            # create new file
            try:
                att = open("%s/%s" % (kit.foldername, "config.txt"), "wt")
            except IOError:
                MessageBox(self, "Unable to save changes", "ERROR: cannot open file %s for writing." % att)
                return

            try:
                # write a comment line, if not already there
                cmt = "# Attribute configuration file auto-generated by GDB Manager"
                print >>att, cmt
                print >>att
                self.writeSortedAttributes(att, kit)

            except Exception, e:
                MessageBox(self, "Unable to save changes", "ERROR during save: %s" % str(e))

            att.close()

        # show save confirmation message, if asked so.
        if showConfirmation:
            MessageBox(self, "Changes saved", "Your changes were successfully saved.")


    def writeSortedAttributes(self, file, kit):
        keys = kit.attributes.keys()
        keys.sort()
        for name in keys:
            if name.startswith("shorts.num-pal.") or name in ["numbers","description","overlay","mask"]:
                print >>file, '%s = "%s"' % (name, kit.attributes[name])
            else:
                print >>file, "%s = %s" % (name, kit.attributes[name])


    """ 
    Returns team name: an ID with helper text, if available.
    """
    def GetTeamText(self, id):
        try:
            return "%s (%s)" % (id, self.teamNames[id])
        except KeyError:
            return "%s" % id


class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, -1, "GDB Manager")
        frame.Show(1)
        self.SetTopWindow(frame)
        return True


if __name__ == "__main__":
    #app = MyApp(redirect=True, filename="output.log")
    #app = MyApp(redirect=True)
    app = MyApp(0)
    app.MainLoop()

