from OFS.Image import File, cookId
from Globals import DTMLFile

manage_addSimplateForm=DTMLFile('dtml/imageAdd', globals(),Kind='Simplate',kind='simplate')
def manage_addSimplate(self,id,file='',title='',precondition='', content_type='',
                   REQUEST=None):
    """Add a new Simplate object.

    Creates a new Simplate object 'id' with the contents of 'file'"""

    id=str(id)
    title=str(title)
    content_type=str(content_type)
    precondition=str(precondition)
    values=[]

    id, title = cookId(id, title, file)

    self=self.this()

    # First, we create the file without data:
    self._setObject(id, Simplate(id,title,'',content_type, precondition, values))

    # Now we "upload" the data.  By doing this in two steps, we
    # can use a database trick to make the upload more efficient.
    if file:
        self._getOb(id).manage_upload(file)
    if content_type:
        self._getOb(id).content_type=content_type

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')


class Simplate(File):
    """We want a File object that we can use python string replacement on."""
    
    meta_type='Simplate'

    _properties=({'id':'title', 'type': 'string'},
                 {'id':'content_type', 'type':'string'},
                 {'id':'values', 'type':'lines'},
                 )
                 
    def __init__(self, id, title, file, content_type='', precondition='',values=[]):
        self.__name__=id
        self.title=title
        self.precondition=precondition
        self.values = values

        data, size = self._read_data(file)
        content_type=self._get_content_type(file, data, id, content_type)
        self.update_data(data, content_type, size)


    def index_html(self, REQUEST, RESPONSE):
        """
        The default view of the contents of a File or Image.

        Returns the contents of the file or image.  Also, sets the
        Content-Type HTTP header to the objects content type.
        """

        unprocessed = File.index_html(self,REQUEST,RESPONSE).replace('%','%%').replace('%%(','%(').replace('%%%(','%%(')

        value_dict = {}

        value_paths = list(self.values)
        value_paths.reverse()
        for path in value_paths:
            if path:
                value_obj = self.restrictedTraverse(path)
                value = value_obj()
                if type(value)==type({}):
                    value_dict.update(value)
                else:
                    raise 'ACK','your value scripts must return dictionaries you MORON!'
        if value_dict:
            return unprocessed % value_dict
        else:
            return unprocessed
