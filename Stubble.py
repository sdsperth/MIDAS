# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 09:10:54 2019

Version Control:
Version     Date        Person  Change
1.1         29Dec19     JMY     Altered feed periods in FeedBudget, therefore had to remove last row in the fp df used in this module
1.2         4Jan20      MRY     Documented me and vol section and changed definitions of dmd and md
1.3         6Jan20      MRY     clip the vol and me df at 0 (dont want negitive me and negitive vol could lead to potential issue) & add vol = 1000/(ri_quality * availability) to be used in pyomo


Known problems:
Fixed   Date        ID by   Problem
       4Jan20       MRY     ^ protien stuff needs to be added still, when the emmisions are done
1.3    4Jan20       MRY     ^ need to clip the vol and me df at 0 (dont want negitive me and negitive vol could lead to potential issue)
       4Jan20       JMY     ^ could possibly convert this numpy to make it more simple 
1.3    4Jan20       JMY     ^need to add vol = 1000/(ri_quality * availability) to be used in pyomo




Stubble:

Total Grain = HI * (above ground) biomass
Leaf + Stem = (1-HI) * biomass
Harvested grain = (1 - spilt%) * Total grain
Spilt grain = spilt% * Total grain
Stubble = Leaf + Stem + Spilt grain

Spilt grain as a proportion of the stubble = (HI * spilt %) / (1 - HI(1 - spilt%))

@author: young
"""
#python modules
import pandas as pd



#midas modules
import FeedBudget as fb
import PropertyInputs as pinp
import Inputs as inp
import StubbleInputs as si
import Crop as crp
import Sensitivity as SA


print('Status:  running stubble')


def stubble_all():
    '''
    Wraps all of stubble into a function that is called in pyomo 
    
    Returns; multiple dicts
        - stubble transfer
        - md and vol
        - harv con limit
    '''
    #########################
    #dmd deterioration      #
    #########################
    
    #create df with feed periods
    fp = pd.DataFrame.from_dict(fb.feed_inputs['feed_periods'],orient='index', columns=['date'])[:-1] #removes last row
    cat_a_st_req=pd.DataFrame()
    cat_b_st_prov=dict() #provide tr ie cat A provides stub b tr - done straight as a dict because value doesn't change for different periods
    cat_b_st_req=dict() #requirment for tr ie cat B requires stub b tr - done straight as a dict because value doesn't change for different periods, this would have to change if trampling was different for periods
    cat_c_st_prov=dict() 
    cat_c_st_req=dict() 
    dmd=pd.DataFrame()
    md=pd.DataFrame()
    ri_quality=pd.DataFrame()
    ri_availability=pd.DataFrame()
    vol=pd.DataFrame()
    cons_limit=pd.DataFrame()
     #function will start here
    stubble_per_grain = crp.stubble_production() #produces dict with stubble production per kg of yield for each grain used in the ri.availability section
    
    for crop in si.stubble_inputs['crop_stub'].keys():
        #add column that is days since harvest in each period (calced from the end date of the period)
        days_since_harv=[]
        for period_num in fp.index:
            if period_num < len(fp)-1:  #because im using the end date of the period, hence the start of the next p, there is an issue for the last period in the df - the last period should ref the date of the first period
                feed_period_date = fp.loc[period_num+1,'date']
                harv_start = pinp.crop['start_harvest_crops'][crop]
                if feed_period_date < harv_start:
                    days_since_harv.append(365 + (feed_period_date - harv_start).days) #add a yr because dates before harvest wont have access to stubble until next yr
                else:  days_since_harv.append((feed_period_date - harv_start).days)
            else: 
                period_num = fp.index[0]
                feed_period_date = fp.loc[period_num,'date']
                harv_start = pinp.crop['start_harvest_crops'][crop]
                if feed_period_date < harv_start:
                    days_since_harv.append(365 + (feed_period_date - harv_start).days) #add a yr because dates before harvest wont have access to stubble until next yr
                else:  days_since_harv.append((feed_period_date - harv_start).days)
        fp['days_%s' %crop]=days_since_harv
        #add the qualntity decline % for each period - used in transfer constraints, need to average the number of days in the period of interest
        quant_decline=[]
        for period_num in fp.index:
                if period_num == 0:
                     if fp.loc[period_num,'date'] < harv_start < fp.loc[period_num+1,'date']:
                         days=fp.loc[period_num,'days_%s' %crop]/2  #divid by two to get the average days on the period to work out average deterioration
                     else: days=fp.loc[len(fp)-1,'days_%s' %crop]+(fp.loc[period_num,'days_%s' %crop]-fp.loc[len(fp)-1,'days_%s' %crop])/2#divid by two to get the average days on the period to work out average deterioration
                elif fp.loc[period_num,'date'] < harv_start < fp.loc[period_num+1,'date']:
                    days=fp.loc[period_num,'days_%s' %crop]/2  #divid by two to get the average days on the period to work out average deterioration
                else: days=fp.loc[period_num-1,'days_%s' %crop]+(fp.loc[period_num,'days_%s' %crop]-fp.loc[period_num-1,'days_%s' %crop])/2
                quant_decline.append(1-(1-si.stubble_inputs['crop_stub'][crop]['quantity_deterioration']/100)**days)
        fp['quant_decline_%s' %crop] = quant_decline
        #add dmd for each component in each period for each crop
        for component, dmd_harv in si.stubble_inputs['crop_stub'][crop]['component_dmd'].items():
            dmd_component=[]
            day=[]
            for period_num in fp.index:
                if period_num == 0:
                     if fp.loc[period_num,'date'] < harv_start < fp.loc[period_num+1,'date']:
                         days=fp.loc[period_num,'days_%s' %crop]/2  #divid by two to get the average days on the period to work out average deterioration
                     else: days=fp.loc[len(fp)-1,'days_%s' %crop]+(fp.loc[period_num,'days_%s' %crop]-fp.loc[len(fp)-1,'days_%s' %crop])/2#divid by two to get the average days on the period to work out average deterioration
                elif fp.loc[period_num,'date'] < harv_start < fp.loc[period_num+1,'date']:
                    days=fp.loc[period_num,'days_%s' %crop]/2  #divid by two to get the average days on the period to work out average deterioration
                else: days=fp.loc[period_num-1,'days_%s' %crop]+(fp.loc[period_num,'days_%s' %crop]-fp.loc[period_num-1,'days_%s' %crop])/2
                day.append(days)
                deterioration_factor = si.stubble_inputs['crop_stub'][crop]['quality_deterioration'][component]
                dmd_component.append((1-(deterioration_factor*days)/100)*dmd_harv)
            fp['%s_%s_dmd' %(crop ,component)]=dmd_component #important as the column names are used in the sim (objective)
        
    
        
        
        ###############
        # M/D & vol   #      
        ###############
        '''
        This section creates a df that contains the M/D for each stubble category for each crop and 
        the equivilant for vol. This is used by live stock.
        
        1) read in stubble component composition, calculated by the sim (stored in an excel file)
        2) converts total dmd to dmd of category 
        3) calcs ri quantity and availabiltiy 
        4) calcs the md of each stubble category (dmd to MD)
        
        '''    
        
        stub_cat_component_proportion=pd.read_excel('Stubble Sim.xlsx',sheet_name=crop,header=None)
        ##quality of each category in each period - muliply quality by proportion of components
        num_stub_cat = len( si.stubble_inputs['crop_stub'][crop]['component_dmd']) #determine number of cats
        comp_dmd_period=fp.iloc[:,-num_stub_cat:] #selects just the dmd from fp df for the crop of interest
        stub_cat_component_proportion.index=comp_dmd_period.columns #makes index = to column names so df mul can be done (quicker than using a loop)
        j=0 #used as scalar for stub available for in each cat below.
        for cat_inx, cat_name in zip(range(len(si.stubble_inputs['crop_stub'][crop]['stub_cat_qual'])), si.stubble_inputs['crop_stub'][crop]['stub_cat_qual'].keys()):
            dmd[crop,cat_name]=comp_dmd_period.mul(stub_cat_component_proportion[cat_inx]).sum(axis=1) #dmd by stub category (a, b, c, d)
            ##calc ri before converting dmd to md
            ri_quality[crop,cat_name]= dmd[crop,cat_name].apply(fb.ri_quality, args=(si.stubble_inputs['clover_propn_in_sward_stubble'],))
            ##ri availability - first calu stubble foo (stub available)
            yield_df = pinp.crop['excel_ranges']['yield']
            stub_foo_harv = yield_df[yield_df>0].loc[crop].mean() * stubble_per_grain[crop] *1000
            stubble_foo = stub_foo_harv * (1 - fp['quant_decline_%s' %crop]) * (1 - j)
            ri_availability[crop,cat_name] = stubble_foo.apply(fb.ri_availability)
            ##combine ri quality and ri availabitily to calc overall vol (potential intake)
            vol[crop,cat_name]=(1/(ri_availability[crop,cat_name].mul(ri_quality[crop,cat_name]))*1000/(1+SA.pi))#.replace(np.inf, 10000) #this produces some inf when ri_quality is 0 (1/0)  
            j+= si.stubble_inputs['crop_stub'][crop]['stub_cat_prop'][cat_name]
            #now convert dmd to M/D
            md[crop,cat_name]=dmd[crop,cat_name].apply(fb.dmd_to_md).mul(1000).clip(lower=0) #mul to convert to tonnes    
    
        ###########
        #trampling#
        ###########
        #for now this is just a single number however the input could be changed to per period, then convert this to a df or array, if this is changed some of the dict below would need to be dfs the stacked - so they acount for period
        tramp_effect=[]
        stub_cat_prop = [] #used in next section but easy to add here in the same loop
        for cat in si.stubble_inputs['crop_stub'][crop]['stub_cat_prop'].keys():
            tramp_effect.append(si.stubble_inputs['crop_stub'][crop]['trampling']/100 * si.stubble_inputs['crop_stub'][crop]['stub_cat_prop'][cat])
            stub_cat_prop.append(si.stubble_inputs['crop_stub'][crop]['stub_cat_prop'][cat])
       
        ###########
        #transfers#   #this is a little inflexible ie you would need to add or remove code if a stubble cat was added or removed
        ###########
        
        cat_a_st_req[crop]= (1/(1-fp['quant_decline_%s' %crop]))*(1+tramp_effect[0])*(1/stub_cat_prop[0])*1000 #*1000 - to convert to tonnes
        cat_b_st_prov[crop] = stub_cat_prop[1]/stub_cat_prop[0]*1000
        cat_b_st_req[crop] = 1000*(1+tramp_effect[1])
        cat_c_st_prov[crop] = stub_cat_prop[2]/stub_cat_prop[1]*1000
        cat_c_st_req[crop] = 1000*(1+tramp_effect[2])
        
        ###############
        #harvest p con# stop sheep consuming more than possible because harvest is not at the start of the period
        ###############
        #how far through each period does harv start? note 0 for each period harv doesn't start in. Used to calc stub consumption limit in harv period
        
        prop=[]
        for i in range(len(fp)):
            if i == len(fp)-1:
                prop.append(1-(fp.loc[i,'days_%s' %crop] / ((fp.loc[0,'date'] - fp.loc[i,'date']).days+365))) 
            else: prop.append(1-(fp.loc[i,'days_%s' %crop] / (fp.loc[i+1,'date'] - fp.loc[i,'date']).days))
        cons_limit[crop]= prop
        cons_limit[crop] =cons_limit[crop].clip(0)
        cons_limit[crop] =  (cons_limit[crop]/(1-cons_limit[crop]))*1000
    
    #collate all the bits for pyomo 
    #return everything as a dict which is acessed in pyomo
    md=pd.concat([md]*len(inp.input_data['sheep_pools']), keys=inp.input_data['sheep_pools']) #add sheep pools here ie add level to df index
    md.columns=pd.MultiIndex.from_tuples(md) #converts to multi index so stacking will have crop and cat as seperate keys 
    md = md.stack().stack().to_dict()    #for pyomo
    
    #return everything as a nested dict which is acessed in pyomo
    stub_vol=pd.concat([vol]*len(inp.input_data['sheep_pools']), keys=inp.input_data['sheep_pools']) #add sheep pools here ie add level to df index
    stub_vol.columns=pd.MultiIndex.from_tuples(stub_vol) #converts to multi index so stacking will have crop and cat as seperate keys 
    stub_vol = stub_vol.stack().stack().to_dict()    #for pyomo
    
    return #return multiple dicts that can be accessed in pyomo    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    