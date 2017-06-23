
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
plt.rcParams.update({'font.size': 22})
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

ax.plot(x, dist.pdf(x), c='black',label=r'Weibull distribution'
        "\n"
        r'$\left(k=%.1f,\ \lambda=%i\right)$' % (k, lam), linewidth = 3)

ax.set_xlim(0, 4)
ax.set_ylim(0, 0.40)

#ax.xlabel('$x$')
#ax.ylabel(r'$p(x|k,\lambda)$')
#ax.title('Power distribution')

ax.set_xlabel(r'\textbf{Unit power [-]}')
ax.set_ylabel(r'\textbf{Probability [-]}')

leg = ax.legend(loc='upper right', fancybox=True, shadow=True, fontsize=24)

leg.legendHandles[0]._sizes = [60]
ax.tick_params(axis='x', which='major', labelsize=22)
ax.tick_params(axis='y', which='major', labelsize=22)

plt.savefig('weibull.pdf', dpi='300', bbox_inches='tight')
#plt.show()

plt.cla()
import matplotlib
fig = plt.figure(1)
ax = plt.subplot(111)
r = matplotlib.patches.Rectangle((.00231, .0), (.02 - .00231), (1./(.02 - .00231)), fill=False, linewidth = 3.0, label = 'Prior $C_r$')
ax.add_artist(r)
ax.set_xlim([0, (0.02+0.0023)])
ax.set_ylim([0, 75])

ax.set_xlabel(r'$\mathbf{C_r}$ [-]}')
ax.set_ylabel(r'\textbf{Probability [-]}')
anyArtist = plt.Line2D((0,1),(0,0), color='k', lw = 3.0)

leg = ax.legend([anyArtist], [r'Uniform distribution for $C_r$'], loc='upper center', fancybox=True, shadow=True, fontsize=24)

plt.savefig('Cr.pdf', dpi='300', bbox_inches='tight')


plt.cla()
import matplotlib
fig = plt.figure(1)
ax = plt.subplot(111)
r = matplotlib.patches.Rectangle((0.2, .0), .6, (1./(.8 - .2)), fill=False, linewidth = 3.0, label = 'Prior $CdA$')
ax.add_artist(r)
ax.set_xlim([0, 1.])
ax.set_ylim([0, 2.7])

ax.set_xlabel(r'$\mathbf{C_dA [-]}$')
ax.set_ylabel(r'\textbf{Probability [-]}')
anyArtist = plt.Line2D((0,1),(0,0), color='k', lw = 3.0)

leg = ax.legend([anyArtist], [r'Uniform distribution'
    "\n"
    r'$C_dA \in \left[0.2, 0.8\right]$'], loc='upper center', fancybox=True, shadow=True, fontsize=24)

for t in leg.texts:
    t.set_multialignment('center')

plt.savefig('CdA.pdf', dpi='300', bbox_inches='tight')


