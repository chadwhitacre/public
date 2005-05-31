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
