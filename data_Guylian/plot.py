import csv
import datetime
import matplotlib.pyplot as plt
import matplotlib
import os
import glob
import pandas
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

#----------Settings for nice LaTeX compatible plots----------------
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
## for Palatino and other serif fonts use:
#rc('font',**{'family':'serif','serif':['Palatino']})
plt.rc('text', usetex=True)
plt.rcParams.update({'font.size': 24})
#------------------------------------------------------------------

path = './'
extension = 'csv'
os.chdir(path)
result = [i for i in glob.glob('*.{}'.format(extension))]

df = pandas.read_csv(result[0], usecols=[2], names = ['speed'])

for csvname in result[1:]:
    df = df.append(pandas.read_csv(result[0], usecols=[2], names = ['speed']))

filterdata = [round(x, 0) for x in df.speed.tolist() if x > 0.5]

x = np.linspace(0,55,1000)


[loc, t, scale] = stats.weibull_min.fit(filterdata, floc=0)

plt.cla()

fig = plt.figure(1)
ax = plt.subplot(111)


a = stats.exponweib.pdf(x, *stats.exponweib.fit(filterdata, 1, 1, scale=scale, loc=loc))
#ax.plot(x, a, label=r'Weibull fit', color='black', linewidth=3.5)
ax.hist(filterdata, bins=np.linspace(0, 55, 55), normed=True, alpha=0.6, label=r'Normalized histogram', color='black');

ax.set_xlabel(r'\textbf{Speed [km/h]}')
ax.set_ylabel(r'\textbf{Frequency [-]}')

leg = ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.25),
          ncol=2, fancybox=True, shadow=True, fontsize=24)

leg.legendHandles[0]._sizes = [60]
ax.tick_params(axis='x', which='major', labelsize=22)
ax.tick_params(axis='y', which='major', labelsize=22)

plt.savefig('weibull.pdf', dpi='300', bbox_inches='tight')
#plt.show()

print("DONE")


plt.show()

