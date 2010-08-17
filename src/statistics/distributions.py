"""
Distributions used in FCS analysis
"""

from numpy import pi, exp, dot, ones, array, sqrt, fabs, tile, sum, prod, diag, zeros, cumsum, reshape
from numpy.linalg import inv, det, cholesky
from numpy.random import random, multivariate_normal
from cdp import mvnpdf, wmvnpdf
#def mvnormpdf(x, mu, va):
#    """
#    multi variate normal pdf, derived from David Cournapeau's em package
#    for mixture models
#    http://www.ar.media.kyoto-u.ac.jp/members/david/softwares/em/index.html
#    """
#    d       = mu.size
#    inva    = inv(va)
#    fac     = 1 /sqrt( (2*pi) ** d * fabs(det(va)))
#
#    y   = -0.5 * dot(dot((x-mu), inva) * (x-mu), 
#                       ones((mu.size, 1), x.dtype))
#
#    y   = fac * exp(y)
#    return y

def mvnormpdf(x, mu, va):
    """
    calculate the multi-variate normal pdf 
    D(x, mu, sigma) -> float
    """
    try:
        n,p = x.shape
    except ValueError:
        n = x.shape
        p = 0
    if p > 0:
        results = mvnpdf(x,mu,va,n)
    else:
        results = array([mvnpdf(x,mu,va)])
    
    return results

def mixnormpdf(x, prop, mu, Sigma):
    """Mixture of multivariate normal pdfs"""
    # print "in mixnormpdf ..."
#    tmp = 0.0
#    for i in range(len(prop)):
#        tmp += prop[i]*mvnormpdf(x, mu[i], Sigma[i])
#    return tmp
    try:
        n,d = x.shape
    except ValueError:
        d = x.shape[0]
        n = 1
        x = x.reshape((1,d))
    try:
        c = prop.shape[0]
    except AttributeError:
        c = 1

    if c == 1: 
        tmp = wmvnpdf(x,prop,mu,Sigma,n)
    else:
        tmp = wmvnpdf(x,prop,mu,Sigma,n*c)
        print tmp.shape
        tmp = sum(reshape(tmp, (n,c)),1)
    return tmp

def mixnormrnd(pi, mu, sigma, k):
    """Generate random variables from mixture of Guassians"""
    xs = []
    for i in range(k):
        j = sum(random() > cumsum(pi))
        xs.append(multivariate_normal(mu[j],sigma[j]))
    return array(xs)  

if __name__ == '__main__':
    x = array([1,0])
    mu = array([5,5])
    sig = array([[1,0],[0, 1]])

    print 'new:', mvnormpdf(x,mu,sig)
    x = array([1,0])
    mu = array([0,0])
    sig = array([[1,.75],[.75, 1]])

    print 'new:', mvnormpdf(x,mu,sig)
    print 'array:', mvnormpdf(array([x,x-1]), mu, sig)
    
    x = array([[1,0],[5,5],[0,0]])
    mu = array([[0,0],[5,5]])
    sig = array([[[1,.75],[.75, 1]],[[1,0],[0,1]]])
    p = array([.5,.5])
    print 'mix:', mixnormpdf(x,p,mu,sig)
    
