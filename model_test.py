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
    DIR_MODEL = './save/'
    file_model_trig = DIR_MODEL + TASK_NAME +'_model_trigger.pkl'
    file_model_arg = DIR_MODEL + TASK_NAME + '_model_arg.pkl'

    triggers, vec_trig, label_trig, args, vec_arg, label_arg = [], [], [], [], [], []
    try:
        triggers, vec_trig, label_trig, args, vec_arg, label_arg = joblib.load(NAME_DATA_FILE)
    except:
        ANN_FILEs = []
        DIR_ALL_FILES = os.listdir(DIR_DATA)
        for file_name in DIR_ALL_FILES:
            if file_name.split('.')[-1] == 'txt':
                ANN_FILEs.append(file_name[:-4])
        corpus = RepoModel(DIR_DATA) # load corpus
        bc = BertClient(ip='127.0.0.1', port=8701, port_out=8702, show_server_config=True) # bert model as service
        for ANN_FILE in ANN_FILEs:
            doc = corpus.documents[ANN_FILE] # get document with key
            ttriggers, tvec_trig, tlabel_trig, targs, tvec_arg, tlabel_arg, label_arg_for_each_trig = get_events_in_mention(doc, bc)
            triggers.extend(ttriggers)
            vec_trig.extend(tvec_trig)
            label_trig.extend(tlabel_trig)
            args.extend(targs)
            vec_arg.extend(tvec_arg)
            label_arg.extend(tlabel_arg)
        print('trigs:', len(vec_trig), 'args:', len(vec_arg))
        joblib.dump([triggers, vec_trig, label_trig, args, vec_arg, label_arg], NAME_DATA_FILE)

    
    print('='*65,'\n>>trigger model testing:')
    model_trig, encoder_trig = joblib.load(file_model_trig)
    acc = test_on_data(model_trig, encoder_trig, vec_trig, label_trig, DIR_DATA, en_verbose = 0)
    print('triggers extraction accuracy: {}'.format(acc))

    print('='*65,'\n>>argument model testing:')
    model_arg, encoder_arg = joblib.load(file_model_arg)
    acc = test_on_data(model_arg, encoder_arg, vec_arg, label_arg, DIR_DATA, en_verbose = 0)
    print('arguements extraction accuracy: {}'.format(acc))


DIR_DATAs = ['data_military-corpus','data_test', 'data_ACE_Chinese','data_ACE_English','data_ACE'] #'data_test', 'data_ACE_English', 'data_ACE_Chinese'
for DIR_DATA in DIR_DATAs:
    testing(DIR_DATA)

    

