from Products.CMFCore.utils import getToolByName


##
# Action helpers (will move to QIHelpers)
##

def uninstallActions(portal, actions):
    """ takes a dictionary of (provider:sequence of (category, action) tuples)s """
    icons_tool = getToolByName(portal, 'portal_actionicons')

    for provider_name in actions.keys():

        # remove from provider
        provider = getToolByName(portal, provider_name)
        default_action_ids = [o.id for o in provider.listActions()]
        remove_action_ids = [a[0] for a in actions[provider_name]]
        selection = [default_action_ids.index(a) for a in default_action_ids
                                                  if a in remove_action_ids]
        provider.deleteActions(selection)

        # remove from portal_actionicons
        for action in actions[provider_name]:
            if action[1]:
                if icons_tool.queryActionInfo(action[0], action[1], None):
                    icons_tool.removeActionIcon(action[0], action[1])


def installActions(portal, actions):
    """ takes a sequence of action dictionaries """
    for provider_name in actions.keys():
        provider = getToolByName(portal, provider_name)
        for action in actions[provider_name]:
            provider.addAction(**action)
