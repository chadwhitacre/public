import os, sys
import urllib
import Globals
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from OFS.SimpleItem import SimpleItem

from Products.Archetypes.Referenceable import Referenceable
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import UniqueObject, getToolByName, format_stx
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# lazy way of configuring this tool
from config import MIN_RATING_VALUE, MAX_RATING_VALUE, STORAGE_CLASS, STORAGE_ARGS

# ##############################################################################
class RatingsTool(PloneBaseTool, UniqueObject, SimpleItem, Referenceable):
    """ """
    id = 'portal_ratings'
    meta_type= 'Ratings Tool'
#    toolicon = 'skins/plone_images/favorite_icon.gif'
    security = ClassSecurityInfo()
    isPrincipiaFolderish = 0
    storage = None
    
    __implements__ = (PloneBaseTool.__implements__, SimpleItem.__implements__, )

    manage_options = ( ({'label':'Overview', 'action':'manage_overview'},) +
                       SimpleItem.manage_options)

    security.declareProtected(CMFCorePermissions.ManagePortal, 'manage_overview')
    manage_overview = PageTemplateFile('www/portal_ratings_manage_overview', globals())
    manage_overview.__name__ = 'manage_overview'
    manage_overview._need__name__ = 0

    manage_main = manage_overview


    def addRating(self, rating, uid):
        mt = getToolByName(self, 'portal_membership')
        if mt.isAnonymousUser():
            raise ValueError, 'Anonymous user cannot rate content'
        member = mt.getAuthenticatedMember()
        username = member.getUserName()

        old_rating = self._getUserRating(uid, username)
        if old_rating is not None:
            self._deleteRating(uid, username)
        return self._addRating(rating, uid, username)

    def getUserRating(self, uid):
        mt = getToolByName(self, 'portal_membership')
        if mt.isAnonymousUser():
            raise ValueError, 'Anonymous user cannot rate content'
        member = mt.getAuthenticatedMember()
        username = member.getUserName()

        return self._getUserRating(uid, username)

    def addHit(self, uid, hit_type=None):
        self._getStorage().addHit(uid,hit_type)

    # Summary statistics: HITS

    # hits for individual item
    def getHitCount(self, uid, hit_type=None):
        return self._getStorage().getHitCount(uid,hit_type)

    # hits for all items
    def getTotalHitCount(self, hit_type=None):
        return self._getHitsSummary(hit_type).getCount()

    def getHitRateTimeInterval(self):
        return HIT_RATE_TIME_INTERVAL
    
    def getHitRate(self, uid, hit_type=None):
        return self._getStorage().getHitCount(uid,hit_type)


    # Summary statistics: RATINGS

    def getMinRating(self):
        return MIN_RATING_VALUE
    
    def getMaxRating(self):
        return MAX_RATING_VALUE

    # rating stats for individual items
    def getRatingCount(self, uid):
        return self._getStorage().getRatingCount(uid)
    
    def getRatingSum(self, uid):
        return self._getStorage().getSum(uid)
    
    def getRatingSumSquared(self, uid):
        return self._getStorage().getSumSquared(uid)
    
    def getRatingMean(self, uid):
        return self._getStorage().getMean(uid)
    
    def getRatingStdDev(self, uid):
        return self._getStorage().getStdDev(uid)

    def getRatingVariance(self, uid):
        return self._getStorage().getVariance(uid)

    # rating stats for all items
    def getTotalRatingCount(self):
        # return a count of rating means
        return self._getStorage().getTotalRatingCount()

    def getRatingMeanCount(self):
        # return a count of rating means
        return self._getStorage().getRatingMeanCount()
    
    def getRatingMeanSum(self):
        # return a sum of rating means
        return self._getStorage().getRatingMeanSum()
    
    def getRatingMeanSumSquared(self):
        # return a sum of rating means squared
        return self._getStorage().getRatingMeanSumSquared()
    
    def getRatingMeanMean(self):
        # return a mean of rating means
        return self._getStorage().getRatingMeanMean()
    
    def getRatingMeanStdDev(self):
        # return a standard deviation of rating means
        return self._getStorage().getRatingMeanStdDev()

    def getRatingMeanVariance(self):
        # return a standard deviation of rating means
        return self._getStorage().getRatingMeanVariance()
    
    def getNoiseVariance(self):
        return self._getStorage().getNoiseVariance()
    
    def getEstimatedRating(self, uid):
        # Use a Bayesian MMSE estimator for DC in white Gaussian noise to
        # estimate the true rating for an item.
        # 
        # Motivation: a small number of very positive or very negative ratings 
        # can make an item look much better or worse than it actually is.  We
        # use a statistical technique to reduce this kind of small number bias.
        # Essentially we assume that true ratings have a Gaussian distribution.
        # Most true ratings are somewhere in the middle, with small numbers
        # very high and small numbers very low.  User ratings for an item are
        # the item's true rating + some Gaussian noise.  User ratings are
        # mostly close to the true rating, with a few much higher and a few
        # much lower.  
        #
        # We estimate a prior distribution of true means and the noise level
        # from all the data.  We then use this prior info for the Bayesian
        # estimator.  See _Fundamentals of Statistical Signal Processing_, by
        # Alan Kay, pp. 316 - 321 for details.
        
        priorMean = self.getRatingMeanMean()
        noiseVariance = self.getNoiseVariance()
        itemMean = self.getRatingMean(uid)
        priorVariance = self.getRatingMeanVariance()
        itemRatings = self.getRatingCount(uid)
        
        if priorMean is None or noiseVariance is None:
            # not enough information to compute a prior -- just return the mean
            if itemMean is None:
                # no data for computing a mean -- return the middle rating
                return 0.5 * (float(self.getMinRating()) + float(self.getMaxRating()))
            return itemMean

        if itemMean is None:
            return priorMean
        
        if priorVariance == 0.0 and noiseVariance == 0.0:
            return itemMean

        
        
        alpha = priorVariance / (priorVariance + noiseVariance/itemRatings)
        return alpha * itemMean + (1.0 - alpha) * priorMean
    

    # private interface
    def _getStorage(self):
        if self.storage is None:
            self.storage = STORAGE_CLASS(**STORAGE_ARGS)
        return self.storage

    def _addRating(self, rating, uid, username):
        # delegate to storage
        self._getStorage().addRating(rating, uid, username)

    def _deleteRating(self, uid, username):
        # delegate to storage
        self._getStorage().deleteRating(uid, username)

    def _getUserRating(self, uid, username):
        # delegate to storage
        return self._getStorage().getUserRating(uid, username)

    def _deleteRatingsFor(self, uid):
        # delegate to storage
        return self._getStorage().deleteRatingsFor(uid)
    
Globals.InitializeClass(RatingsTool)