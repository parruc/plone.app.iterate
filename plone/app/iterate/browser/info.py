"""
$Id: base.py 1808 2007-02-06 11:39:11Z hazmat $
"""

from zope.interface import implements
from zope.component import getUtility

from zope.viewlet.interfaces import IViewlet

from DateTime import DateTime

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import ITranslationServiceTool

from plone.app.iterate.util import get_storage
from plone.app.iterate.interfaces import keys

from plone.app.iterate.relation import WorkingCopyRelation

from plone.memoize.instance import memoize

class BaseInfoViewlet( BrowserView ):
    
    implements( IViewlet )
    
    def __init__( self, context, request, view, manager ):
        super( BaseInfoViewlet, self ).__init__( context, request )
        self.__parent__ = view
        self.view = view
        self.manager = manager
        
    def update( self ):
        pass
    
    def render(self):
        raise NotImplementedError(
            '`render` method must be implemented by subclass.')
    
    @memoize
    def created( self ):
        time = self.properties.get( keys.checkout_time, DateTime() )
        util = getUtility(ITranslationServiceTool)
        return util.ulocalized_time(time, None, self.context, domain='plonelocales')

    @memoize
    def creator( self ):
        user_id = self.properties.get( keys.checkout_user )
        membership = getToolByName( self.context, 'portal_membership' )
        if not user_id:
            return membership.getAuthenticatedMember()
        return membership.getMemberById( user_id )
        
    @memoize
    def creator_url( self ):
        creator = self.creator()
        portal_url = getToolByName( self.context, 'portal_url' )
        return "%s/author/%s" % ( portal_url(), creator.getId() )
        
    @memoize
    def creator_name( self ):
        creator = self.creator()
        return creator.getProperty('fullname') or creator.getUserName()

    @property
    @memoize
    def properties( self ):
        wc_ref = self._getReference()
        return get_storage( wc_ref )

    def _getReference( self ):
        raise NotImplemented
        
class BaselineInfoViewlet( BaseInfoViewlet ):
    
    render = ViewPageTemplateFile('info_baseline.pt')

    def working_copy( self ):
        return self.context.getBRefs( WorkingCopyRelation.relationship )[0]

    def _getReference( self ):
        refs = self.context.getBackReferenceImpl( WorkingCopyRelation.relationship )
        wc_ref = refs[0]
        return wc_ref
        
class CheckoutInfoViewlet( BaseInfoViewlet ):
    
    render = ViewPageTemplateFile('info_checkout.pt')
    
    def baseline( self ):
        return self.context.getReferences( WorkingCopyRelation.relationship )[0]
    
    def _getReference( self ):
        refs = self.context.getReferenceImpl( WorkingCopyRelation.relationship )
        wc_ref = refs[0]
        return wc_ref
        