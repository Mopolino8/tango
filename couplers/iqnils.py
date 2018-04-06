import numpy as np
from scipy.linalg import qr, solve_triangular
import os
import json


class IQNILS:
    def __init__(self, parameters):
        if not type(parameters) is dict:
            with open(os.path.join(parameters, "settings.txt")) as f:
                parameters = json.load(f)

        self.added = False
        self.rref = np.array([])
        self.xtref = np.array([])
        self.v = np.matrix([])
        self.w = np.matrix([])
        self.minsignificant = parameters["minsignificant"]
        self.omega = parameters["omega"]

    def add(self, x, xt):
        r = xt - x
        if self.added:
            dr = r - self.rref
            dxt = xt-self.xtref
            if self.v.shape[1]:
                self.v = np.concatenate((dr, self.v), 1)
                self.w = np.concatenate((dxt, self.w), 1)
            else:
                self.v = np.matrix(np.reshape(dr, (-1, 1)))
                self.w = np.matrix(np.reshape(dxt, (-1, 1)))
        self.rref = r
        self.xtref = np.array(xt)
        self.added = True

    def predict(self, r):
        # Remove columns resulting in small diagonal elements in R
        singular = True
        print(self.v.shape)
        while singular and self.v.shape[1]:
            rr = qr(self.v, mode='r')
            diag = np.diagonal(rr)
            m = min(diag)
            if m < self.minsignificant:
                i = np.argmin(diag)
                self.v = np.delete(self.v, i, 1)
                self.w = np.delete(self.w, i, 1)
            else:
                singular = False
        # Calculate return value if sufficient data available
        if self.v.shape[1]:
            # Interface Quasi-Newton with approximation for the inverse of the Jacobian from a least-squares model
            qq, rr = qr(self.v, mode='reduced')
            print(rr.shape)
            c = solve_triangular(rr, np.transpose(qq) * (-r))
            dx = self.w * c + r
        else:
            if self.added:
                dx = self.omega * r
            else:
                raise RuntimeError("No information to predict")
        return dx

    def initializestep(self):
        self.rref = np.array([])
        self.xtref = np.array([])
        self.v = np.matrix([])
        self.w = np.matrix([])

    def finalizestep(self):
        print(self.added)
        if self.added:
            self.added = False
        else:
            raise RuntimeError("No information added during step")
