from AccessControl.Permissions import add_documents_images_and_files
import Simplate
import OFS

def initialize(context):

    context.registerClass(
        Simplate.Simplate,
        permission=add_documents_images_and_files,
        constructors=(('simplateAdd',Simplate.manage_addSimplateForm),
                      Simplate.manage_addSimplate),
        )