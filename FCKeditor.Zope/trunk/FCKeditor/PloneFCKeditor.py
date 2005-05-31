#BOILERPLATE###################################################################
#                                                                             #
#  This package wraps FCKeditor for use in the Zope web application server.   #
#  Copyright (C) 2005 Chad Whitacre <http://www.zetadev.com/>                 #
#                                                                             #
#  This library is free software; you can redistribute it and/or modify it    #
#  under the terms of the GNU Lesser General Public License as published by   #
#  the Free Software Foundation; either version 2.1 of the License, or (at    #
#  your option) any later version.                                            #
#                                                                             #
#  This library is distributed in the hope that it will be useful, but        #
#  WITHOUT ANY WARRANTY; without even the implied warranty of                 #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser    #
#  General Public License for more details.                                   #
#                                                                             #
#  You should have received a copy of the GNU Lesser General Public License   #
#  along with this library; if not, write to the Free Software Foundation,    #
#  Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA                #
#                                                                             #
###################################################################BOILERPLATE#
from Products.FCKeditor.FCKeditor import FCKeditor

class PloneFCKeditor(FCKeditor):
    """Wrap FCKeditor for use in Plone.

    Instances of this class are not meant to be stored, but to be used on the
    fly from Scripts (Python). Import it like this:

        from Products.FCKeditor import PloneFCKeditor

    For an example, see:

        skins/fckeditor_plone/wysiwyg_fckeditor.py

    """



    # Override PloneFCKeditor templates to support tabindex.
    # ======================================================

    COMPATIBLE = """\
<div>
    <input type="hidden"
           id="%(InstanceName)s"
           name="%(InstanceName)s"
           value=%(Value)s />
    <input type="hidden"
           id="%(InstanceName)s___Config"
           value="%(ConfigQuerystring)s" />
    <iframe id="%(InstanceName)s___Frame"
            src="%(BasePath)seditor/fckeditor.html?InstanceName=%(InstanceName)s&Toolbar=%(ToolbarSet)s"
            width="%(Width)s" height="%(Height)s"
            frameborder="no" scrolling="no"
            tabindex="%(tabindex)s"></iframe>
</div>"""

    INCOMPATIBLE = """\
<div>
    <textarea name="%(InstanceName)s"
              rows="4" cols="40"
              style="width: %(Width)s; height: %(Height)s;"
              wrap="virtual"
              tabindex="%(tabindex)s">
        %(Value)s
    </textarea>
</div>"""



    # Set up some setters.
    # ====================
    # We can't mess with non-method attrs directly from restricted Python.

    def SetConfig(self, key, val):
        self.Config[key] = val

    def SetProperty(self, key, val):
        self.__dict__[key] = val
