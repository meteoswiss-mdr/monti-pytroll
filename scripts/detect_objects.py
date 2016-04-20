if False:

    import numpy as np
    from scipy import ndimage
    import matplotlib.pyplot as plt
    
    np.random.seed(1)
    n = 10
    l = 256
    im = np.zeros((l, l))
    points = l*np.random.random((2, n**2))
    im[(points[0]).astype(np.int), (points[1]).astype(np.int)] = 1
    im = ndimage.gaussian_filter(im, sigma=l/(4.*n))
    mask = (im > im.mean()).astype(np.float)
    mask += 0.1 * im
    img = mask + 0.2*np.random.randn(*mask.shape)
    hist, bin_edges = np.histogram(img, bins=60)
    bin_centers = 0.5*(bin_edges[:-1] + bin_edges[1:])
    binary_img = img > 0.5
    plt.figure(figsize=(11,4))
    plt.subplot(131)
    plt.imshow(img)
    plt.axis('off')
    plt.subplot(132)
    plt.plot(bin_centers, hist, lw=2)
    plt.axvline(0.5, color='r', ls='--', lw=2)
    plt.text(0.57, 0.8, 'histogram', fontsize=20, transform = plt.gca().transAxes)
    plt.yticks([])
    plt.subplot(133)
    plt.imshow(binary_img, cmap=plt.cm.gray, interpolation='nearest')
    plt.axis('off')
    plt.subplots_adjust(wspace=0.02, hspace=0.3, top=1, bottom=0.1, left=0, right=1)
    plt.show()
    
else:

    import numpy as np
    from scipy import ndimage
    import matplotlib.pyplot as plt
    import pickle
    from skimage import morphology
    
    rgb = pickle.load( open( "RGB201508081415.p", "rb" ) )
    #rgb = pickle.load( open( "RGB201508081230.p", "rb" ) )
    print type(rgb)
    mask = pickle.load( open( "mask_dam_201508081415.p", "rb" ) )
    #mask = pickle.load( open( "mask_dam_201508081230.p", "rb" ) )
    print rgb
    
    print mask
    print -mask
    a = morphology.remove_small_objects(mask, 100,connectivity=2)
    
    b = morphology.remove_small_objects(-a, 1000)
    
    # Remove small white regions
    open_img = ndimage.binary_opening(mask)
    # Remove small black hole
    close_img = ndimage.binary_closing(open_img)    

    # Remove small white regions
    open_img1 = ndimage.binary_opening(-b)
    # Remove small black hole
    close_img1 = ndimage.binary_closing(open_img1)    

    
    fig = plt.figure()
    ax = plt.subplot(231)
    ax.imshow(mask)
    ax.axis('off')
    ax.set_title("mask")
    ax1 = plt.subplot(232)
    ax1.imshow(rgb)
    ax1.axis('off')
    ax1.set_title("rgb")
    ax2 = plt.subplot(233)
    ax2.imshow(a)
    ax2.axis('off')
    ax2.set_title("(a)Remove small clouds",fontsize=9)
    ax3 = plt.subplot(234)
    ax3.imshow(b)
    ax3.axis('off') 
    ax3.set_title("(b)Remove no_clouds (a)",fontsize=9)
    ax4 = plt.subplot(235)   
    ax4.imshow(close_img)
    #ax4.contour(close_img, [0.5], linewidths=1, colors='g')
    ax4.axis('off') 
    ax4.set_title("(c) Opening&Closing rgb",fontsize=9)
    ax5 = plt.subplot(236)   
    ax5.imshow(close_img1)
    #ax5.contour(close_img1, [0.5], linewidths=1, colors='g')
    ax5.axis('off') 
    ax5.set_title("(d) Opening&Closing result removed (b)",fontsize=9)
    fig.show()  
    
    plt.savefig("201507071625_obj_detection.png")
    
    
    if False:
        np.random.seed(1)
        n = 10
        l = 256
        im = np.zeros((l, l))
        points = l*np.random.random((2, n**2))
        im[(points[0]).astype(np.int), (points[1]).astype(np.int)] = 1
        print im
        im = ndimage.gaussian_filter(im, sigma=l/(4.*n))
        print im
        mask = (im > im.mean()).astype(np.float)
        print mask
        img = mask + 0.3*np.random.randn(*mask.shape)
        binary_img = img > 0.5
        # Remove small white regions
        open_img = ndimage.binary_opening(binary_img)
        # Remove small black hole
        close_img = ndimage.binary_closing(open_img)
        plt.figure(figsize=(12, 3))
        l = 128
        plt.subplot(141)
        plt.imshow(binary_img[:l, :l], cmap=plt.cm.gray)
        plt.axis('off')
        plt.subplot(142)
        plt.imshow(open_img[:l, :l], cmap=plt.cm.gray)
        plt.axis('off')
        plt.subplot(143)
        plt.imshow(close_img[:l, :l], cmap=plt.cm.gray)
        plt.axis('off')
        plt.subplot(144)
        plt.imshow(mask[:l, :l], cmap=plt.cm.gray)
        plt.contour(close_img[:l, :l], [0.5], linewidths=2, colors='r')
        plt.axis('off')
        plt.subplots_adjust(wspace=0.02, hspace=0.3, top=1, bottom=0.1, left=0, right=1)
        plt.show()

