from Products.Archetypes.ReferenceEngine import Reference

class RatingsReference(Reference):
    def beforeSourceDeleteInformTarget(self):
        uid = self.getSourceObject().UID()
        ratings_tool = self.getToolByName('portal_ratings')
        ratings_tool._deleteRatingsFor(uid)