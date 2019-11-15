#model fit
import os
import numpy as np
from sklearn.externals import joblib
from bert_serving.client import BertClient
from bratreader.repomodel import RepoModel
from sklearn.preprocessing import LabelEncoder
from model_com import create_base_network, get_events, fit_on_data, test_on_data, get_events_in_mention


def testing(DIR_DATA): 
    print('\n\nTesting {}>>>\ndata importing:'.format(DIR_DATA))
    TASK_NAME = DIR_DATA
    NAME_DATA_FILE = TASK_NAME+'_data_import'+'.save'

    ttriggers, tvec_trig, tlabel_trig, targs, tvec_arg, tlabel_arg = joblib.load(NAME_DATA_FILE)
    
    triggers, vec_trig, label_trig, args, vec_arg, label_arg = [], [], [], [], [], []
    
    for idx in range(len(tlabel_trig)):
        if tlabel_trig[idx] != 'NULL':
            triggers.append(ttriggers[idx])
            vec_trig.append(tvec_trig[idx])
            label_trig.append(tlabel_trig[idx])
            
    for idx in range(len(tlabel_arg)):
        if tlabel_arg[idx] != 'NULL':
            args.append(targs[idx])
            vec_arg.append(tvec_arg[idx])
            label_arg.append(tlabel_arg[idx])
    
    joblib.dump([triggers, vec_trig, label_trig, args, vec_arg, label_arg], 'data_dump/NO_NULL/'+NAME_DATA_FILE)


DIR_DATAs = ['data_ACE']
for DIR_DATA in DIR_DATAs:
    testing(DIR_DATA)

    

