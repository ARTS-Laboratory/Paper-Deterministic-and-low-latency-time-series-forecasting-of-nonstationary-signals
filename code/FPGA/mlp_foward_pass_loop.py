# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""



import IPython as IP
IP.get_ipython().magic('reset -sf')

import numpy as np
import scipy as sp
import pandas as pd
from scipy import fftpack, signal # have to add 
import matplotlib as mpl
import matplotlib.pyplot as plt
import sklearn as sk
import time as time
import sklearn as sklearn
from sklearn import linear_model
from sklearn import pipeline
from sklearn import datasets
from sklearn import multiclass
from sklearn import neural_network
import json as json
import pickle as pickle

cc = plt.rcParams['axes.prop_cycle'].by_key()['color']

plt.close('all')

#%% 


def relu(x):
    return x * (x > 0)

# sigmoid function
def logistic(x,deriv=False):
    if(deriv==True):
        return x*(1-x)
    return 1/(1+np.exp(-x))








#%% define parameters

# window_length = 0.1     # window lengtht in number of data points
sample_Rate = 50000         # DAQ sample rate in S/s. This lines up with the clock speed for simplicity
n_features= 50   # number of features used in training the ANN
prediction_steps = 25 #5000
noise_level = 0.01
n_computation_ticks = 1 # set the number of ticks needed to solve the forward pass



n_samples = 10 # number of training samples

#%% Build the signal


freq_hz = 2000
omega = freq_hz*2*np.pi

ticks = np.arange(0,400)
tt = ticks/sample_Rate
xx_clean = np.sin(tt*omega)
xx_clean[200::] = xx_clean[200::] * 1.5

#plot the signal
fig, ax = plt.subplots(constrained_layout=True)
ax.plot(tt, xx_clean,':o')
ax.set_xlabel('time (s)')
ax.set_ylabel('potential (V)')
def x2time(x):
    return x *40000
def x2ticks(x):
    return x 
secax = ax.secondary_xaxis('top', functions=(x2time, x2ticks))
secax.set_xlabel('clock ticks (#)')
secax.grid(True)
plt.show()



#%% Train the model

xx = xx_clean+np.random.randn(xx_clean.shape[0])*noise_level

current_step = 0
tt_X_train = []
tt_y_train = []
X_train = []
y_train = []
for i in range(n_samples):
    tt_X_train.append(tt[current_step:current_step+n_features])
    X_train.append(xx[current_step:current_step+n_features])
    y_train.append(xx[current_step+n_features+prediction_steps])
    tt_y_train.append(tt[current_step+n_features+prediction_steps])
    current_step = current_step + n_computation_ticks
    
    
X_train = np.asarray(X_train)
y_train = np.asarray(y_train)
tt_y_train = np.asarray(tt_y_train)
tt_X_train = np.asarray(tt_X_train) 


mlp = sklearn.neural_network.MLPRegressor(hidden_layer_sizes=(20),solver='adam',random_state=1, max_iter=500,activation='relu')
mlp = mlp.fit(X_train, y_train)

plt.figure()
for i in range(n_samples):
    plt.plot(tt_X_train[i],X_train[i,:]+i*0.5,'--',color=cc[i])
    plt.plot(tt_y_train[i],y_train[i]+i*0.5,'o',color=cc[i])

#%% test the model at 1 point

# for i in range(0,400,3):
current_step = 50
X_test = xx[current_step:current_step+n_features]
X_test = np.expand_dims(X_test, axis=0)
ticks_X_test = ticks[current_step:current_step+n_features]
y_test = xx[current_step+n_features+prediction_steps]
ticks_y_test = ticks[current_step+n_features+prediction_steps]

# perform inference using sklearn
y_predicted = mlp.predict(X_test)
print(y_predicted[0])

# perform inference by hand
coef = mlp.coefs_
intercept = mlp.intercepts_
l1 = relu(np.matmul(X_test,coef[0])+intercept[0]) 
y_predicted_direct = np.matmul(l1,coef[1])+intercept[1]
print(y_predicted_direct[0][0])


plt.figure()
plt.plot(ticks,xx,'.-k',label='true data')
plt.stem(ticks_X_test,X_test[0,:],label='digitized data')
plt.plot(current_step+n_features+prediction_steps,y_predicted[0],'rx',fillstyle='none',markersize=15,label='inferred value')
plt.xlabel('clock ticks (#)')
plt.ylabel('potential (V)')
plt.grid(True)
plt.legend(framealpha=1,loc=2)
plt.tight_layout()
    
    # plt.savefig('plots/'+str(i),dpi=100)
    # plt.close('all')



#%% Solve the entire data set


y = []
tick_y = []
for current_step in range(0,324):
    X_test = xx[current_step:current_step+n_features]
    X_test = np.expand_dims(X_test, axis=0)
    ticks_X_test = ticks[current_step:current_step+n_features]
    y_test = xx[current_step+n_features+prediction_steps]
    ticks_y_test = ticks[current_step+n_features+prediction_steps]
    
    # perform inference using sklearn
    y_predicted = mlp.predict(X_test)
    y.append(y_predicted[0])
    tick_y.append(current_step+n_features+prediction_steps)

y = np.asarray(y)
tick_y = np.asarray(tick_y)
error = xx[tick_y]-y

plt.figure()
plt.subplot(211)
plt.plot(ticks,xx,'.-k',lw=0.6,label='true data')
plt.plot(tick_y,y,'rx-',lw=0.6,fillstyle='none',markersize=5,label='inferred value')
plt.plot(tick_y,np.abs(error))
plt.xlabel('clock ticks (#)')
plt.ylabel('potential (V)')
plt.xlim([-5,405])
plt.grid(True)
plt.legend(framealpha=1,ncol=2,loc=2)




plt.subplot(212)
plt.plot(tick_y,np.abs(error))
plt.xlabel('clock ticks (#)')
plt.ylabel('error (|V|)')
plt.xlim([-5,405])
plt.grid(True)

plt.tight_layout()

plt.savefig('signal with error',dpi=300)



#%% Save the trained model

# data = {'coef':coef,'intercept':intercept,'xx':xx,}
# pickle.dump(data,open('data/weights.pkl','wb'))

np.savetxt("data/MLP_1_C_0.csv", coef[0], delimiter=",")
np.savetxt("data/MLP_1_C_1.csv", np.expand_dims(coef[1][:,0],axis=0), delimiter=",")
np.savetxt("data/MLP_1_B_0.csv", np.expand_dims(intercept[0],axis=0), delimiter=",")
np.savetxt("data/MLP_1_B_1.csv", intercept[1], delimiter=",")
np.savetxt("data/MLP_1_xx.csv", np.expand_dims(xx,axis=0), delimiter=",")

# data_2 = {'coef_1':coef[0].tolist(),
#           'coef_2':coef[1].tolist(),
#           'intercept_1':intercept[0].tolist(),
#           'intercept_2':intercept[1].tolist()}  

# #data_2 = {'coef':[l.tolist() for l in coef],'intercept':[l.tolist() for l in intercept]}  
# with open('data/weights.json', 'w') as outfile:
#     json.dump(data_2, outfile)  







#%% test the matrix multiply

intermediate_layer_1 = xx[0:50]@coef[0]
intermediate_layer_2 = coef[0].T@xx[0:50]

intermediate_layer_1-intermediate_layer_2


















