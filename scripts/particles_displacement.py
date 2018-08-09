#https://tonysyu.github.io/animating-particles-in-a-flow.html
def particles_displacement( u_func, v_func, method, dt, pts, size_x, size_y, wind_source ):
    
    import sympy   # does include e.g. integrate
    #from sympy.abc import x, y
    import numpy as np
    from matplotlib import mlab
    from scipy import integrate
    from math import floor        
    
    def euler(f, pts, dt):
        vel = np.asarray([f(xy) for xy in pts])
        return pts + vel * dt
    
    def rk4(f, pts, dt):
        new_pts = [mlab.rk4(f, xy, [0, dt])[-1] for xy in pts]
        return new_pts
    
    def ode_scipy(f, pts, dt):
        new_pts = [integrate.odeint(f, xy, [0, dt])[-1] for xy in pts]
        return new_pts
    
    available_integrators = dict(euler=euler, rk4=rk4, scipy=ode_scipy)
    
    def displace_func_from_velocity_funcs(u_func, v_func, method='rk4'):
        """Return function that calculates particle positions after time step.
    
        Parameters
        ----------
        u_func, v_func : functions
            Velocity fields which return velocities at arbitrary coordinates.
        method : {'euler' | 'rk4' | 'scipy'}
            Integration method to update particle positions at each time step.
        """

        def velocity(xy, t=0):
            """Return (u, v) velocities for given (x, y) coordinates."""
            # Dummy `t` variable required to work with integrators
            # Must return a list (not a tuple) for scipy's integrate functions.
            x_px=int(floor(xy[0]//size_x))    # floor is equivalent to using float as index in old python
            y_px=int(floor(xy[1]//size_y))    # floor is equivalent to using float as index in old python
            
            if x_px<u_func.shape[0] and y_px<u_func.shape[1] and x_px>=0 and y_px>=0:
                return [u_func[x_px,y_px], v_func[x_px,y_px]]
                
            else:
                return [0,0]
    
        odeint = available_integrators[method]
        
        def displace(xy, dt):
            return odeint(velocity, xy, dt)
    
        return displace
    
    if wind_source=="cosmo":
          u_func=np.flipud(u_func)
          v_func=np.flipud(v_func)
    displace=displace_func_from_velocity_funcs(u_func, v_func, method=method)
    return displace(pts, dt)














