# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 21:00:13 2019

module: exriment module - this is the module that runs everything and controls kv's

@author: young
"""
#import datetime
import pandas as pd
from pyomo.environ import *

import RotationPhases as rps #this won't be here when sa is hooked up properly
import UniversalInputs as uinp
import PropertyInputs as pinp 
import CoreModel as core
import CropPyomo as crppy
import RotationPyomo as rotpy 
import Sensitivity as sen 


#######################
#key options          #
#######################
#eg flk structure, mach option etc - this is set the default, can be changed in runs via saa
        
        

#########################
#Exp loop               #
#########################

##read in exp log
# exp_data = pd.read_excel('exp.xlsx')
# for row in range(len(exp_data)):
#     for column in exp_data:
#         value = exp_data.loc[exp_data.index[row], column]
#         sen[column]=value
        ##call sa functions - assigns sa variables to relevant inputs
    # uinp.univeral_inp_sa()
    # pinp.property_inp_sa()
    # ##call core model function, must call them in the correct order (core must be last)
    # rotpy.rotationpyomo()
    # crppy.croppyomo_local()
    # core.coremodel_all()




##the stuff below will be superseeded with stuff above 

con_error=[]
con_correct=[]
##create loop for exp
# for i in rps.lo_bound.keys():#(range(1)): #maybe this should be looping through an exp sheet in excel
# # for i in (range(1)): #maybe this should be looping through an exp sheet in excel
# #     print('Starting exp loop')
# #     #define any SA - this module will have to import sensitivity module then other module will import sensitivity therefore sensitivity shouldn't inport pre calc modules
#     rps.lo_bound[i]=0.1 #('A', 'C', 'N', 'OF', 'm')
    

#     #call core model function, must call them in the correct order (core must be last)
#     rotpy.rotationpyomo()
#     crppy.croppyomo_local()
#     core.coremodel_all()
#     if core.coremodel_test_var[-1]==1:
#         con_error.append(i)
#     print(core.coremodel_test_var[-1])
    
#     rps.lo_bound[i]=0
import random
for p in range(1):
        
    # for j,i in zip(range(2000,2054), rps.lo_bound.keys()):#(range(1)): #maybe this should be looping through an exp sheet in excel
    bounded_rots=[]
    for i in random.sample(range(2441),1):#(range(1)): #maybe this should be looping through an exp sheet in excel
    # # # for i in (range(1)): #maybe this should be looping through an exp sheet in excel
    # # #     print('Starting exp loop')
    # # #     #define any SA - this module will have to import sensitivity module then other module will import sensitivity therefore sensitivity shouldn't inport pre calc modules
        
        k=list(rps.lo_bound.keys())[i] #('A', 'C', 'N', 'OF', 'm')
        bounded_rots.append(k)
        # rps.lo_bound['GX3NPo']=6 #('A', 'C', 'N', 'OF', 'm')
        rps.lo_bound['GA5ENw']=6 #('A', 'C', 'N', 'OF', 'm')
        # rps.lo_bound['GNEPb']=6 #('A', 'C', 'N', 'OF', 'm')
    # print(rps.lo_bound)
    
    #call core model function, must call them in the correct order (core must be last)
        rotpy.rotationpyomo()
        print('rps done')
        crppy.croppyomo_local()
        print('crop done')
        core.coremodel_all()
        print('cpre done')
        if core.coremodel_test_var[-1]==1:
            con_error.append(k)
        else: 
            con_correct.append(k)
        print(core.coremodel_test_var[-1])
    
        rps.lo_bound[k]=0
    
    
    
    
    
    
    
    
    
    
    