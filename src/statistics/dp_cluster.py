'''
Created on Oct 30, 2009

@author: Jacob Frelinger
'''

from distributions import mvnormpdf
from numpy import array
from component import Component
from util import modesearch
from enthought.traits.api import HasTraits, List, Float, Array, Dict, Int
from warnings import warn


class DPCluster(HasTraits, Component):
    '''
    Single component cluster in mixture model
    '''
    pi = Float()
    mu = Array()
    sigma = Array()
    def __init__(self, pi, mu, sig):
        '''
        DPCluster(pi,mu,sigma)
        pi = cluster weight
        mu = cluster mean
        sigma = cluster variance/covariance
        '''
        self.pi = pi
        self.mu = mu
        self.sigma = sig
        
    def prob(self, x):
        '''
        DPCluster.prob(x):
        returns probability of x beloging to this mixture compoent
        '''
        return self.pi * mvnormpdf(x, self.mu, self.sigma)
    


class DPMixture(HasTraits):
    '''
    collection of compoents that describe a mixture model
    '''
    clusters = List(DPCluster)
    m = Array
    s = Array
    def __init__(self, clusters, m = False, s = False):
        '''
        DPMixture(clusters)
        cluster = list of DPCluster objects
        '''
        self.clusters = clusters
        if m is not False:
            self.m = m
        if s is not False:
            self.s = s
        
    def prob(self, x):
        '''
        DPMixture(x)
        returns a list of probabilities of x being in each component of the mixture
        '''
        return array([i.prob(x) for i in self.clusters])
    
    def classify(self, x):
        '''
        DPMixture.classify(x):
        returns the classification (which mixture) x is a member of
        '''
        probs = self.prob(x)
        return probs.argmax(0)
    
    def mus(self, normed=False):
        '''
        DPMixture.mus():
        returns an array of all cluster means
        '''
        if normed:
            return array([i.nmu for i in self.clusters])
        else:
            return array([i.mu for i in self.clusters])
    
    def sigmas(self, normed=False):
        '''
        DPMixture.sigmas():
        returns an array of all cluster variance/covariances
        '''
        if normed:
            return array([i.nsigma for i in self.clusters])
        else:
            return array([i.sigma for i in self.clusters])
    
    def pis(self):
        '''
        DPMixture.pis()
        return an array of all cluster weights/proportions
        '''
        return array([i.pi for i in self.clusters])
    
    def make_modal(self, tol=1e-5, maxiter=20):
        try:
            modes,cmap = modesearch(self.pis(), self.mus(True), self.sigmas(True), tol, maxiter)
            return ModalDPMixture(self.clusters, cmap, modes, self.m, self.s)

        except AttributeError:
            warn("trying to make modal of a mixture I'm not sure is normalized.\nThe mode finding algorithm is designed for normalized data.\nResults may be unexpected")
            modes,cmap = modesearch(self.pis(), self.mus(), self.sigmas(), tol, maxiter)
            return ModalDPMixture(self.clusters, cmap, modes)   
        
        
    

class ModalDPMixture(DPMixture, HasTraits):
    '''
    collection of modal compoents that describe a mixture model
    '''
    clusters = List(DPCluster)
    cmap = Dict(Int, List(Int))
    modes = Dict(Int, Array)
    m = Array
    s = Array
    def __init__(self, clusters, cmap, modes, m=False, s=False):
        '''
        DPMixture(clusters)
        cluster = list of DPCluster objects
        cmap = map of modal clusters to component clusters
        '''
        self.clusters = clusters
        self.cmap = cmap
        self.modemap = modes

        if m is not False:
            self.m = m
        if s is not False:
            self.s = s
        
    def prob(self,x):
        rslt = []
        for j in self.cmap.keys():
            rslt.append(sum([self.clusters[i].prob(x) for i in self.cmap[j]]))
            
        return array(rslt)
    
    def modes(self):
        lst = []
        for i in self.modemap.itervalues():
            try:
                lst.append((array(i)*self.s)+self.m)
            except AttributeError:
                lst.append(i)
        return array(lst)        

