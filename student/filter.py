# ---------------------------------------------------------------------
# Project "Track 3D-Objects Over Time"
# Copyright (C) 2020, Dr. Antje Muntzinger / Dr. Andreas Haja.
#
# Purpose of this file : Kalman filter class
#
# You should have received a copy of the Udacity license together with this program.
#
# https://www.udacity.com/course/self-driving-car-engineer-nanodegree--nd013
# ----------------------------------------------------------------------
#

# imports
import numpy as np

# add project directory to python path to enable relative imports
import os
import sys
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
import misc.params as params 

class Filter:
    '''Kalman filter class'''
    def __init__(self):
        # load parameters from params.py
        self.q = params.q
        self.dt = params.dt
        self.dim_state = params.dim_state

    def F(self):
        # system matrix 6x6
        return np.matrix([[1, 0, 0, self.dt, 0, 0],
                          [0, 1, 0, 0, self.dt, 0],
                          [0, 0, 1, 0, 0, self.dt],
                          [0, 0, 0, 1, 0, 0],
                          [0, 0, 0, 0, 1, 0],
                          [0, 0, 0, 0, 0, 1]])

    def Q(self):
        # process noise covariance Q 6x6 - discretiziced!
        q1 = self.dt * self.q
        q2 = (self.dt**2 * self.q) / 2
        q3 = (self.dt**3 * self.q) / 3
        return np.matrix([[q3, 0, 0, q2, 0, 0],
                          [0, q3, 0, 0, q2, 0],
                          [0, 0, q3, 0, 0, q2],
                          [q2, 0, 0, q1, 0, 0],
                          [0, q2, 0, 0, q1, 0],
                          [0, 0, q2, 0, 0, q1]])

    def predict(self, track):
        F = self.F()

        # perform prediction
        x = F * track.x                             # state prediction
        P = F * track.P * F.transpose() + self.Q()  # covariance prediction

        # return predicted state x and covariance P with associated measurement
        return track.set_x(x), track.set_P(P)

    def update(self, track, meas):
        H = meas.sensor.get_H(track.x)       # Jacobian H at current point x

        # perform update
        gamma = self.gamma(track, meas)                      # residual - nonlinear with h(x)
        S = self.S(track, meas, H)                           # covariance of residual using Jacobian H
        K = track.P * H.transpose() * np.linalg.inv(S)       # Kalman gain
        x = track.x + K * gamma                              # state update
        P = (np.identity(self.dim_state) - K * H) * track.P  # covariance update

        # track.update_attributes(meas)

        # return updated state x and covariance P with associated measurement
        return track.set_x(x), track.set_P(P)
    
    def gamma(self, track, meas):
        # calculate gamma using nonlinear measurement function h(x)
        gamma = meas.z - meas.sensor.get_hx(track.x)
        return gamma

    def S(self, track, meas, H):
        # calculate covariance of residual using Jacobian H
        S = (H * track.P * H.transpose()) + meas.R
        return S
