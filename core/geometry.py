from math import cos, sin, radians

def polar_to_cartesian(r, theta, degrees_mode=True):
    if degrees_mode:
        theta = radians(theta)
    return r * cos(theta), r * sin(theta)
