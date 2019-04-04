import numpy as np
import matplotlib.pyplot as plt

from astropy.convolution import *
from astropy.modeling.models import Gaussian2D

import scipy.ndimage as ndimage
import numpy as np

import pickle

n_box = 11
#n_box =  5

if False:
    # Small Gaussian source in the middle of the image
    gauss = Gaussian2D(1, 0, 0, 2, 2)
    # Fake data including noise
    x = np.arange(-100, 101)
    y = np.arange(-100, 101)
    x, y = np.meshgrid(x, y)
    data_2D = gauss(x, y) + 0.1 * (np.random.rand(201, 201) - 0.5)
    vmin=-0.01
    vmax=0.08
    origin='lower'
    n_box=11
else:
    data_2D = pickle.load( open( "/opt/users/lel/PyTroll/scripts/Test_satellite.p" ,"rb") )
    data_2D = data_2D[200:300, 250:350]
    if False:
        data_2D = (data_2D-data_2D.mean())/data_2D.std()
        vmin=-3.5
        vmax=1.5
    else:
        vmin=210
        vmax=235
    origin='upper'

(nx,ny) = data_2D.shape

print "min/max/mean", data_2D.min(), data_2D.max(), data_2D.mean()

# Setup kernels, including unity kernel for original image
# Choose normalization for linear scale space for MexicanHat

k = 0.002 / MexicanHat2DKernel(n_box).array.sum()

plot_type = 1
x_line = 30
#x_line = 40
y_line = 50
#y_line = 40

kernels = [#TrapezoidDisk2DKernel(n_box, slope=0.2),
           #Tophat2DKernel(n_box),
           #Gaussian2DKernel(n_box),
           Box2DKernel(n_box),
           #n_box ** 2 * MexicanHat2DKernel(n_box),
           20 * MexicanHat2DKernel(n_box)]
           #AiryDisk2DKernel(n_box)]

#print kernels

if plot_type == 1:
    #fig, axes = plt.subplots(nrows=2, ncols=3)
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(16,16))
    im = axes.flat[0].imshow(data_2D, vmin=vmin, vmax=vmax, origin=origin, interpolation='None')
    #axes.flat[0].set_yticklabels([])
    #axes.flat[0].set_xticklabels([])
    axes.flat[0].set_title('original data', fontsize=12)
elif plot_type == 3:
    vmin = -10
    vmax =  10
    #fig, axes = plt.subplots(nrows=2, ncols=3)
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(16,16))
    data_diff = data_2D[2:,2:]-data_2D[:-2,:-2]
    im = axes.flat[0].imshow(data_diff, vmin=vmin, vmax=vmax, origin=origin, interpolation='None')
    #axes.flat[0].set_yticklabels([])
    #axes.flat[0].set_xticklabels([])
    axes.flat[0].set_title('data[2:,2:]-data[:-2,:-2]', fontsize=12)

elif plot_type == 2:
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(18,9))
    axes[0].step(np.arange(ny), data_2D[x_line,:], where='mid', label='org data')
    axes[1].step(np.arange(nx), data_2D[:,y_line], where='mid', label='org data')
    axes[0].set_title("x="+str(x_line), fontsize=12)
    axes[1].set_title("y="+str(y_line), fontsize=12)

# Plot kernels
#for kernel, ax in zip(kernels, axes.flat[1:]):
#    
#    print "... calculate ", kernel.__class__.__name__ 
#
#    if (kernel.__class__.__name__ != "MexicanHat2DKernel") and (kernel.__class__.__name__ != "Box2DKernel"):
#        smoothed = convolve(data_2D, kernel)
#        print kernel.__class__.__name__, kernel.array.sum()
#        title = kernel.__class__.__name__

for i in [1,2,3]:
    if i == 1:

        k = np.ones([5,3])
        k = k / k.sum()
        title =  "ndimage.convolve 5x3"
        print title 
        smoothed = ndimage.convolve(data_2D, k, mode='nearest')

    if i == 2:

        if False:
            title = "gaussian_laplace"
            print "title"
            #smoothed = data_2D + ndimage.gaussian_laplace(data_2D, 3, mode='nearest') * 10.
            smoothed = ndimage.gaussian_laplace(data_2D, 3, mode='nearest') * 10.

        if True:
            #sigma=1/2.*np.array([4.5,3.0])  # no artefacts more for shifted fields
            sigma=1/3.*np.array([4.5,3.0])  # conserves a bit better the maxima
            title = "gaussian_filter "+str(sigma)
            print "... image 2: ", title
            smoothed = ndimage.filters.gaussian_filter(data_2D, sigma, mode='nearest')

    if i == 3:

        if True:
            sigma=1/2.*np.array([4.5,3.0])  # no artefacts more for shifted fields
            #sigma=1/3.*np.array([4.5,3.0])  # conserves a bit better the maxima
            title = "gaussian_filter "+str(sigma)
            print "title", title
            smoothed = ndimage.filters.gaussian_filter(data_2D, sigma, mode='nearest')

        if False:
            k = np.ones([7,5])
            out=-0.2
            k[0,:] = out
            k[6,:] = out
            k[:,0] = out
            k[:,4] = out
            print k
            k = k / k.sum()
            title = "ndimage.convolve 5x3 mod A"
            print "title", title
            smoothed = ndimage.convolve(data_2D, k, mode='nearest')

        if False:
            k = np.ones([5,3])
            corner = 0.5
            k[0,0] = corner
            k[4,0] = corner
            k[0,2] = corner
            k[4,2] = corner
            print k
            k = k / k.sum()
            title =  "ndimage.convolve 5x3 mod B"
            print "title", title 
            smoothed = ndimage.convolve(data_2D, k, mode='nearest')

        if False:
            k = 1.3 * np.ones([5,3])
            line2 = 0.6
            k[0,:] = line2
            k[4,:] = line2
            k[:,0] = line2
            k[:,2] = line2
            corner = 0.2
            k[0,0] = corner
            k[4,0] = corner
            k[0,2] = corner
            k[4,2] = corner
            print k
            k = k / k.sum()
            title =  "ndimage.convolve 5x3 mod C"
            print "title", title 
            smoothed = ndimage.convolve(data_2D, k, mode='nearest')

        if False:
            title =  "fourier filter"

            # try a fourier filter to filter out the high frequencies
            # http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_imgproc/py_transforms/py_fourier_transform/py_fourier_transform.html
            # -----
            # http://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_imgproc/py_transforms/py_fourier_transform/py_fourier_transform.html
            # http://paulbourke.net/miscellaneous/imagefilter/
            f = np.fft.fft2(data_2D)
            fshift = np.fft.fftshift(f)
            rows, cols = data_2D.shape
            crow,ccol = rows/2 , cols/2

            # Box mask: delete high frequencies -> low pass filter == smoothing 
            #mask = np.zeros((rows,cols),np.uint8)
            #mask[crow-30:crow+30, ccol-30:ccol+30] = 1
            #fshift = fshift * mask

            if False:
                # Circle mask: delete high frequencies -> low pass filter == smoothing 
                mask = np.zeros((rows,cols),np.uint8)
                # Create index arrays to z
                I,J=np.meshgrid(np.arange(rows),np.arange(cols))
                # calculate distance of all points to centre
                dist=np.sqrt((I-crow)**2+(J-ccol)**2)
                # Assign value of 1 to those points where dist<cr:
                cr = 13
                mask[np.where(dist < cr)]=1
                title = title+' rad='+str(cr)
                if False:
                    plt.imshow(mask, interpolation='none')
                    plt.show()
                    quit()
                fshift = fshift * mask

            # Gauss mask: delete high frequencies -> low pass filter == smoothing 
            if False:

                if False:
                    import scipy.stats as st
                    nsig=9
                    # """Returns a 2D Gaussian kernel array."""
                    kernlen=rows
                    interval = (2*nsig+1.)/(kernlen)
                    x = np.linspace(-nsig-interval/2., nsig+interval/2., kernlen+1)
                    kern1d = np.diff(st.norm.cdf(x))
                    kernel_raw = np.sqrt(np.outer(kern1d, kern1d))
                    #mask = kernel_raw/kernel_raw.sum()
                    mask = kernel_raw/kernel_raw.max()
                else:
                    nsig = 2.3*np.array([3.0,4.5])
                    mask = np.zeros((rows,cols))
                    mask[rows//2, cols//2] = 1.0
                    import scipy.ndimage.filters as fi
                    # 2D Gaussian kernel array = dirac(gauss)
                    kernel_raw = fi.gaussian_filter(mask, nsig)
                    mask = kernel_raw/kernel_raw.max()
                if False:
                    plt.imshow(mask, interpolation='none')
                    plt.show()
                    quit()
                title = title+' sigma='+str(nsig)
                fshift = fshift * mask

            # Box: delete low frequencies -> edge detection 
            if False:
                cr=20
                fshift[crow-cr:crow+cr, ccol-cr:ccol+cr] = 0

            f_ishift = np.fft.ifftshift(fshift)
            smoothed = np.fft.ifft2(f_ishift)
            print type(smoothed), smoothed.shape, smoothed.dtype
            smoothed = np.abs(smoothed)

            if True:
                vmin =  smoothed.min()
                vmax =  smoothed.max()

            print "title", title


        #kernel = Box2DKernel(n_box)
        #smoothed = convolve(data_2D, kernel)
        #print kernel.__class__.__name__, kernel.array.sum()
        #title = kernel.__class__.__name__

        #kernel = 25 * MexicanHat2DKernel(3)
        ##kernel = 200 * MexicanHat2DKernel(11)
        #smoothed = data_2D - convolve(data_2D, kernel)
        #print kernel.__class__.__name__, kernel.array.sum()
        #title = kernel.__class__.__name__

    if plot_type == 1:
        ax = axes.flat[i]
        im = ax.imshow(smoothed, vmin=vmin, vmax=vmax, origin=origin, interpolation='None')
        ax.set_title(title, fontsize=12)
    if plot_type == 2:
        im = axes[0].plot(smoothed[x_line,:], label=title)
        im = axes[1].plot(smoothed[:,y_line], label=title)
    if plot_type == 3:
        ax = axes.flat[i]
        smoothed_diff = smoothed[2:,2:] - smoothed[:-2,:-2]
        im = ax.imshow(smoothed_diff, vmin=vmin, vmax=vmax, origin=origin, interpolation='None')
        ax.set_title(title, fontsize=12)


    #ax.set_yticklabels([])
    #ax.set_xticklabels([])

if plot_type==1 or plot_type==3:
    cax = fig.add_axes([0.9, 0.1, 0.03, 0.8])
    fig.colorbar(im, cax=cax)
    plt.subplots_adjust(left=0.05, right=0.85, top=0.95, bottom=0.05)
if plot_type==2:
    axes[0].legend(loc='best')
    axes[1].legend(loc='best')

plt.show()
    
