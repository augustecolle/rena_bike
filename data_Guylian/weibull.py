
import numpy as np
from scipy.stats import dweibull
from matplotlib import pyplot as plt

#----------------------------------------------------------------------
# This function adjusts matplotlib settings for a uniform feel in the textbook.
# Note that with usetex=True, fonts are rendered with LaTeX.  This may
# result in an error if LaTeX is not installed on your system.  In that case,
# you can set usetex to False.

#------------------------------------------------------------
# Define the distribution parameters to be plotted
k_values = [0.5, 1, 2, 2]
lam_values = [1, 1, 1, 2]
linestyles = ['-', '--', ':', '-.', '--']
mu = 0
x = np.linspace(-10, 10, 1000)

#----------Settings for nice LaTeX compatible plots----------------
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
## for Palatino and other serif fonts use:
#rc('font',**{'family':'serif','serif':['Palatino']})
plt.rc('text', usetex=True)
plt.rcParams.update({'font.size': 24})
#------------------------------------------------------------------



plt.cla()

fig = plt.figure(1)
ax = plt.subplot(111)


#------------------------------------------------------------
# plot the distributions
k = 1.7
lam = 1.1
dist = dweibull(k, 0, lam)
x = np.linspace(0, 4, 1000)

ax.plot(x, dist.pdf(x), c='black',label=r'Weibull distribution $\left(k=%.1f,\ \lambda=%i\right)$' % (k, lam), linewidth = 3.5)

ax.set_xlim(0, 4)
ax.set_ylim(0, 0.40)

#ax.xlabel('$x$')
#ax.ylabel(r'$p(x|k,\lambda)$')
#ax.title('Power distribution')

ax.set_xlabel(r'\textbf{Unit power [-]}')
ax.set_ylabel(r'\textbf{Frequency [-]}')

leg = ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.25),
          ncol=2, fancybox=True, shadow=True, fontsize=24)

leg.legendHandles[0]._sizes = [60]
ax.tick_params(axis='x', which='major', labelsize=22)
ax.tick_params(axis='y', which='major', labelsize=22)

plt.savefig('weibull.pdf', dpi='300', bbox_inches='tight')
#plt.show()

