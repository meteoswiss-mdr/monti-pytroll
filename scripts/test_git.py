import matplotlib.pyplot as plt
import numpy as np
a = 1
b = 1
t = np.arange(0,2*np.pi, 0.1)
x = 16*np.sin(t)**3
y = 13*np.cos(t)-5*np.cos(2*t)-2*np.cos(3*t)-np.cos(4*t)
plt.text(-10,0 , "we love Locarno Monti", fontsize=20)
plt.text(15,-15, "E.L", fontsize=20)
plt.plot(x,y,'b')
print "This is the result of 1+1: ",a+b
plt.show()
