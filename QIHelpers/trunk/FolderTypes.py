def installFolderTypes(portal, our_folder_types, out):
    props = portal.portal_properties.site_properties
    try:
        old_tabs_value = list(props.use_folder_tabs)
    except:
        old_tabs_value = [props.use_folder_tabs]
    for folder_type in our_folder_types:
        if folder_type not in old_tabs_value:
            old_tabs_value.append(folder_type)
            props.use_folder_tabs = old_tabs_value
