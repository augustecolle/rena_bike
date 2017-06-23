import numpy as np
import scipy.optimize
import pylab as pl
from scipy import interpolate

#motor parameters from motor experiments on HT3540 motor

Vb      = 4.444     #[V]
Ra      = 0.267     #[Ohm] winding resistance
Req     = 62.338    #active losses Rm_ev in paralel with Rl_v
Ieq     = 0.429     #current losses, Im_hf + Il_f
ke      = [1.182, 1.029, 0.951, 0.898, 0.852, 0.826, 0.796, 0.772, 0.680]    #[V/rad] motor constant
omega   = [15.818, 21.064, 25.185, 29.285, 33.238, 36.558, 40.123, 43.092, 56.287]  #[rad]
R_wheel = 0.699     #[mm] measure this (with tire)

fke     = interpolate.interp1d(omega, ke, bounds_error=False, fill_value=(0.015,0.015)) #change the fill value with more experiments

def fke(par):
    return 0.680

def getData(traject, segnum=None):
    if (segnum == None):
        segnum      = len(traject.segments)
    segments    = [None]*segnum
    segcount    = 0
    eff_m       = []
    for h in range(segnum): 
        msmntnum            = len(traject.segments[h].measurements)
        if(msmntnum > 1):
            segment_timestamps  = [None]*msmntnum
            segment_rho         = [traject.segments[h].rho]*msmntnum
            segment_pm          = [None]*msmntnum
            segment_vg          = [None]*msmntnum
            segment_va          = [None]*msmntnum
            segment_slope       = [traject.segments[h].slope]*msmntnum
            efficiencies        = [None]*msmntnum
            for i in range(msmntnum):
                segment_timestamps[i]   = traject.segments[h].measurements[i].time
                segment_vg[i]           = traject.segments[h].measurements[i].speed
                amps                    = traject.segments[h].measurements[i].amps
                volts                   = traject.segments[h].measurements[i].volts
                omega                   = segment_vg[i]/R_wheel 
                #print(omega)
                segment_pm[i]           = amps*volts - (Ra*amps**2 + (fke(omega)*omega)**2/Req + fke(omega)*omega*Ieq + Vb*amps) #see "A Simple Equivalent Circuit for Efficiency Calculation of Brushless DC Motors"
                efficiencies[i]         = segment_pm[i]/(amps*volts)
                eff_m.append(efficiencies[i])
                segment_va[i]           = traject.segments[h].measurements[i].sqprvwsigned #squared projected windvelocity, already signed
            segment = [ segment_timestamps, segment_rho, segment_pm, segment_vg, segment_va, segment_slope ]
            segment = [np.array(x) for x in segment]
            #print(np.std(segment_vg))
            if (np.std(segment_vg) < 1.2 and np.mean(segment_vg) > 4.):
                segments[segcount]  = segment
            segcount = segcount + 1
    #pl.scatter(range(len(eff_m)), eff_m)
    #pl.show()
    return [x for x in segments if x is not None]

# make fake data for n segments
def getFakeData(n):
    np.random.seed(43237)
    segments = [None]*n # initialize list that will contain n segments
    for i in range(n):
        segment_timesteps  = np.random.randint(5,10) # assume between 5 and 10 timesteps for this segment
        segment_timestamps = np.arange(0,segment_timesteps,1) # s, some "actual" time data
        segment_rho        = 1.   + 0.00*np.random.random(segment_timesteps) # kg/m^3, put some variation on rho
        segment_pm         = 200. + 0.00*(np.random.random(segment_timesteps)-0.5) # W, mechanical power
        segment_vg         = 10. + np.random.normal(0,1e-10,segment_timesteps) # m/s, ground speed
        segment_va         =  5. + np.random.normal(0,1e-10,segment_timesteps) # m/s, air speed projected on ground speed, can be negative!
        segment_slope      = np.random.normal(0,0.01,segment_timesteps) # dimless, slope, height/distance
        segment = [ segment_timestamps, segment_rho, segment_pm, segment_vg, segment_va, segment_slope ]
        segments[i] = segment
    return segments

# estimate the power given segments
# and the parameters, see errorf for
# explanation about x
def estimatePower(x,segments):
    m    = 100. # kg, mass of cyclist+bicycle
    g    = 9.81 # gravitation
    cyclistUnitPower = 100 # W
    CdA   = x[0]
    Cr    = x[1]
    PUcyc = x[2]
    #print("WINDP")
    #print([ -0.5*rho*CdA*vg*va for [_,rho,_,vg,va,slope] in segments]) 
    return np.array([ -0.5*rho*CdA*vg*va + Cr*vg*m*g + m*g*vg*slope - PUcyc*cyclistUnitPower for [_,rho,_,vg,va,slope] in segments ])

# loglikelihood of priors,
# if the variables are independent
# you can multiply the different probabilities
# or equivalently add the log(probabilities)
def lnlikelihoodPriors(CdA,Cr,PUcyc):
    lnprior = 0.

    # CdA prior
    CdAmin = 0.1
    CdAmax = 1.2
    if ( CdAmin <= CdA <= CdAmax):
        lnprior += np.log(1./(CdAmax-CdAmin)) # np.log is ln
        #print(lnprior)
    else:
        #print("inf in CdA")
        lnprior += -np.inf

    # Cr prior
    Crmin = 0.00231 #original
    #Crmax = 0.0133 #original
    Crmax = 0.02
    if ( Crmin <= Cr <= Crmax ):
        lnprior += np.log(1./(Crmax-Crmin)) # np.log is ln
        #print(lnprior)
    else:
        #print("inf in Cr")
        lnprior += -np.inf

    # P cyclist prior
    k = 1.7
    l = 1.0
    #print(k/l*(PUcyc/l)**(k-1.)*np.exp( -(PUcyc/l)**k))
    #print(k/l)
    #print((PUcyc/l)**(k-1.))
    #print(np.exp( -(PUcyc/l)**k))
    #print("----------------------------")
    #print(k)
    #print(l)
    #print(PUcyc)
    if (PUcyc >= 0.):
        lnprior += np.log( k/l ) + np.log((PUcyc/l)**(k-1.)) - (PUcyc/l)**k 
    else:
        lnprior += -np.inf
    #--------------------------------------
    #@Auguste
    #sigma = np.sqrt(0.005)
    #mu = 1.
    #scaleF = 1./(0.0133 - 0.00231)
    #if (PUcyc >= 0.5):
    #    lnprior += np.log(1./np.sqrt(2.*np.pi*sigma**2)) - (PUcyc - mu)**2/(2.*sigma**2)
    #    print(lnprior)
    #else:
    #    print("inf in PUcyc")
    #    lnprior += -np.inf
    return lnprior

# error function to minimize
# x is a vector of parameters
# x[0] : CdA, m^2 drag coefficient * A
# x[1] : Cr, dimless rolling coefficient
# x[2] : cyclist power, dimensionless has to be multiplied with "cyclistunitpower" to get SI units
# sigma: W^-1, this is a measure of the allowed discrepancy between known motor power and inferred moter power
#        small sigma: strong fitting, priors are weak, large sigma, loose fitting, priors are strong
def errorf(x,segments,sigma):
    CdA   = x[0]
    Cr    = x[1]
    PUcyc = x[2]
    pm_guess    = estimatePower(x,segments)
    print("guess:")
    print(CdA, Cr, PUcyc)
    pm_measured = [ s[2] for s in segments ]
    pm_var = sum([ np.sum( (pm_guess[i] - pm_measured[i])**2 ) for i in range(len(segments)) ])
    L = 0.5/sigma**2*pm_var - lnlikelihoodPriors(CdA,Cr,PUcyc)
    #print("Loss function : {:.6e}".format(L))

    return L

def main():
    #segments = getFakeData(6)
    segments = getData()
    x0 = [ 0.6,0.005,1]
    sigma = 0.001 # if this is very small, strong fitting <-> weaker priors. Very large weaker fitting <-> stronger priors
    res = scipy.optimize.minimize(errorf,x0,args=(segments,sigma))
    print("optimal parameters, loss function = {:.6e} ".format(errorf(res.x,segments,sigma)))
    print("succes : {:}".format(res.success))
    print("------------------- ")
    print("| CdA  : {:.3f}     ".format(res.x[0]))
    print("| Cr   : {:.3f}     ".format(res.x[1]))
    print("| Pcyc : {:.3f}     ".format(res.x[2]))
    
    pm_guessf    = np.concatenate(estimatePower(res.x,segments))
    pm_measuredf = np.concatenate([ s[2] for s in segments ])
    fig =pl.figure()
    fig.subplots_adjust(left=0.16)
    ax = fig.add_subplot(111)
    ax.plot(pm_guessf,marker='s',color="firebrick",lw=3,ls="dashed",label="fit")
    ax.plot(pm_measuredf,marker='o',color="black",lw=3,ls="solid",label="measured")
    ax.legend(frameon=False,fontsize=20)
    ax.set_ylabel("Power (W)",fontsize=20)
    pl.show()

def test(segments):
    #segments = getFakeData(6)
    x = [ 0.6,0.005,1]
    Pest = estimatePower(x,segments)
    #print(Pest)

if __name__=="__main__":
    main()
    #test()
