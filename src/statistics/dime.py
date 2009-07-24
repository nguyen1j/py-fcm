from __future__ import division
from statistics.distributions import mvnormpdf, mixnormpdf
from numpy import array, dot, log2, zeros, sum

class DiME(object):
    """
    DiME analysis object
    
    """
    
    def __init__(self, x, pi, mu, sigma, cmap=None):
        """
        DiME(pi, mu, sigma, cmap=None):
        x: data points
        pi: mixing proportions
        mu: means of distributions
        sigma: covariances
        cmap: a dictionary of modal cluster to component clusters, defaults to
            None. If none perform analysis on component cluster level.
        """
        
        self.pi = pi
        self.mu = mu
        self.sigma = sigma
        self.data = x
        self.k = x.shape[1] # dimension
        self.n = x.shape[0] # number of points
        if cmap == None:
            self.c = len(pi) # number of clusters
            self.cpi = pi
        else:
            self.c = len(cmap.keys())
            self.cpi = []
            for clst in cmap.keys():
                self.cpi.append( sum([pi[j] for j in cmap[clst]]))
        self.cmap = cmap
        
        
    def d(self, drop = []):
        """
        calculate discriminitory information
        """
        ids = []
        if type(drop) is type(1): # are we dropping single col?
            for i in range(self.k):
                if i != drop:
                    ids.append(i)
        else: # we're dropping a list
            for i in range(self.k):
                if i not in drop:
                    ids.append(i)
        
        x = self.data[:,ids]
        ids = array(ids)
        mus = [m[ids] for m in self.mu]
        sigmas = [sig[ids,:][:,ids] for sig in self.sigma]
        
        # calculate -1*\log_2(\frac{\delta_c}{\Delta_c})
        # where \detla_c =  \frac{\gamma_c}\{1-\gamma_c}\Sum_{e != c}\gamma_e F_{c,e}
        # \Delta_c = \gamma_c \Sum_{e=1:C} \gamma_e F_{c,e}
        # where F_{c,e} = \int f_c(x)*f_e(x) dx
        # and  where f_c(x) = \Sum_{J in c} \frac{\pi_j}{\gamma_c}N(x|\mu_j,\Sigma_j)
        
        # we calculate F_{c,e} as P(mu_c-mu_e ~ N(0, sigma_c+sigma_e))
        # since we're going to be calculating with P(x in j) a lot precalculate it all
        # once in advance, since we'll need it all at least once and in general multiple times
        # TODO: parallelize here
        
        size = len(self.pi)
        f = zeros((size, size), dtype='float64')
        #zero = zeros(x.shape[1])
        for i in range(size):
            for j in range(i,size):
                f[i, j] = f[j, i] = mvnormpdf(mus[i], mus[j], sigmas[i]+sigmas[j])
                
        F = zeros((self.c, self.c), dtype='float64')
        for i in range(self.c):
            for j in range(i, self.c):
                tmp = 0
                for fclust in self.cmap[i]:
                    for tclust in self.cmap[j]:
                        tmp += (self.pi[fclust]/self.cpi[i])*(self.pi[tclust]/self.cpi[j])*f[fclust,tclust]
                F[i,j] = F[j,i] = tmp
        

        #calculate \delta_c and \Delta_c
        dc = zeros(self.c)
        Dc = zeros(self.c)
        sum_ex = 0 # use this later to caculate complete sum in \Gamma_c
        for mclust in self.cmap.keys():
            normalizing = self.cpi[mclust]/(1-self.cpi[mclust])
            tmp = []
            for i in self.cmap.keys():
                if i == mclust:
                    pass
                else:
                    tmp.append(i)
            sum_ex = sum([self.cpi[i]*F[mclust,i] for i in tmp])
            dc[mclust] = normalizing*sum_ex
            Dc[mclust] = self.cpi[mclust]*(sum_ex+(self.cpi[mclust]*F[mclust,mclust]))
        return -1*log2(dc/Dc)
    
    def rdrop(self, drop):
        try:
            return 100*self.d(drop)/self.d_none
        except AttributeError:
            self.d_none = self.d()
            return 100*self.d(drop)/self.d_none