def installFolderTypes(portal, folder_types, out):
    props = portal.portal_properties.site_properties
    try:
        old_tabs_value = list(props.use_folder_tabs)
    except:
        old_tabs_value = [props.use_folder_tabs]
    for folder_type in folder_types:
        if folder_type not in old_tabs_value:
            old_tabs_value.append(folder_type)
            props.use_folder_tabs = old_tabs_value
    out.write("Installed our folder types.\n")

def installRootProps(portal, ROOT_PROPS, out):
    for prop in [p['id'] for p in portal._properties]:
        if prop in ROOT_PROPS.keys():
            portal._setPropValue(prop, ROOT_PROPS[prop])
    out.write("Updated properties on portal object.\n")
    