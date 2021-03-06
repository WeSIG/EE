#model fit
import os
import numpy as np
from sklearn.externals import joblib
from bert_serving.client import BertClient
from bratreader.repomodel import RepoModel
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from model_com import create_base_network, get_events, fit_on_data, test_on_data, get_events_in_mention

from keras import backend as K



def training(DIR_DATA): 
    print('\ndata importing:')
    TASK_NAME = DIR_DATA
    NAME_DATA_FILE = TASK_NAME+'_data_import'+'.save'

    DIR_MODEL = './save/'
    file_model_trig = DIR_MODEL + TASK_NAME +'_model_trigger.pkl'
    file_model_arg = DIR_MODEL + TASK_NAME + '_model_arg.pkl'
    triggers, vec_trig, label_trig, args, vec_arg, label_arg = [], [], [], [], [], []
    try:
        triggers, vec_trig, label_trig, args, vec_arg, label_arg = joblib.load(NAME_DATA_FILE)
        print('trigs:', len(label_trig), 'args:', len(label_arg))
    except:
        corpus = RepoModel(DIR_DATA) # load corpus
        bc = BertClient(ip='127.0.0.1', port=8701, port_out=8702, show_server_config=True) # bert model as service
        
        # obtain all the files list
        ANN_FILEs = []
        DIR_ALL_FILES = os.listdir(DIR_DATA)
        for file_name in DIR_ALL_FILES:
            if file_name.split('.')[-1] == 'txt':
                ANN_FILEs.append(file_name[:-4])
        for ANN_FILE in ANN_FILEs:
            doc = corpus.documents[ANN_FILE] # get document with key
            ttriggers, tvec_trig, tlabel_trig, targs, tvec_arg, tlabel_arg, label_arg_for_each_trig = get_events_in_mention(doc, bc)
            triggers.extend(ttriggers)
            vec_trig.extend(tvec_trig)
            label_trig.extend(tlabel_trig)
            args.extend(targs)
            vec_arg.extend(tvec_arg)
            label_arg.extend(tlabel_arg)

        joblib.dump([triggers, vec_trig, label_trig, args, vec_arg, label_arg], NAME_DATA_FILE)
        print('trigs:', len(label_trig), 'args:', len(label_arg))
    
    N_batchs =[len(label_trig), 8192, 4096, 2048, 1024, 512, 32, 16, 8, 4, 2, 1]
    N_batchs =[64, 32, 8, 4, 2, 1]
    lrs = [1e-3,1e-5]
    N_trains = 4
    N_epochs = 1
    


    print('='*65,'\n>>argument model training:')
    try:
        triggers, vec_trig, label_trig = None, None, None
        triggers, vec_trig, label_trig, args, vec_arg, label_arg = joblib.load(NAME_DATA_FILE)
        triggers, vec_trig, label_trig = None, None, None
        model_arg, encoder_arg = joblib.load(file_model_arg)
        acc_pre = test_on_data(model_arg, encoder_arg, vec_arg, label_arg, DIR_DATA, en_verbose = 0)
    except:
        encoder_arg = LabelEncoder()
        encoder_arg.fit(label_arg)
        # model define
        input_dim = np.asarray(vec_arg).shape[1]
        N_classes = len(set(label_arg))
        model_arg = create_base_network(input_dim, N_classes)
        acc_pre = 0
    
    X_train, X_test, Y_train, Y_test = train_test_split(vec_arg, label_arg, random_state=0)
    for lr in lrs:
        for N_batch in N_batchs:
            Times_training, N_batch, en_verbose = N_trains, N_batch, 1
            N_epoch = N_epochs # max(N_epochs, int(np.floor(np.sqrt(10*N_batch))))
            for times in range(1, Times_training):
                the_lr = lr/times
                model_arg, encoder_arg, his = fit_on_data(X_train, Y_train, model_arg, encoder_arg, the_lr, N_batch = N_batch, N_epoch = N_epoch, en_verbose = en_verbose)
                #model_arg, encoder_arg, his = fit_on_data(vec_arg, label_arg, model_arg, encoder_arg, the_lr, N_batch = N_batch, N_epoch = N_epoch, en_verbose = en_verbose)
                print('acc:{}'.format(his.history['acc'][-1]))
                val_acc = test_on_data(model_arg, encoder_arg, X_test, Y_test, DIR_DATA, en_verbose = en_verbose)
                #val_acc = test_on_data(model_arg, encoder_arg, vec_arg, label_arg, DIR_DATA, en_verbose = en_verbose)
                joblib.dump([model_arg,encoder_arg], '{}_{:.5f}_{:.5f}_{:.5f}_{:.5f}.pkl'.format(
                    file_model_arg[0:-4], his.history['acc'][-1], val_acc, the_lr, N_batch)) # save the model to disk
                if val_acc > acc_pre:
                    acc_pre = val_acc
                    joblib.dump([model_arg,encoder_arg], '{}.pkl'.format(file_model_arg[0:-4])) # save the model to disk
                else:
                    break

    
    

    print('='*65,'\n>>trigger model training:')
    try:
        args, vec_arg, label_arg = None, None, None
        triggers, vec_trig, label_trig, args, vec_arg, label_arg = joblib.load(NAME_DATA_FILE)
        args, vec_arg, label_arg = None, None, None
        model_trig, encoder_trig = joblib.load(file_model_trig)
        acc_pre = test_on_data(model_trig, encoder_trig, vec_trig, label_trig, DIR_DATA, en_verbose = 0)
    except:
        # model define
        input_dim = np.asarray(vec_trig).shape[1]
        N_classes = len(set(label_trig))
        model_trig = create_base_network(input_dim, N_classes)
        encoder_trig = LabelEncoder()
        encoder_trig.fit(label_trig)
        acc_pre = 0
    
    X_train, X_test, Y_train, Y_test = train_test_split(vec_trig, label_trig, random_state=0)
    for N_batch in N_batchs:
        for lr in lrs:
            Times_training, N_batch, en_verbose = N_trains, N_batch, 1
            N_epoch = N_epochs # max(N_epochs, int(np.floor(np.sqrt(10*N_batch))))
            for times in range(1, Times_training):
                the_lr = lr/times
                model_trig, encoder_trig, his = fit_on_data(X_train, Y_train, model_trig, encoder_trig, the_lr, N_batch = N_batch, N_epoch = N_epoch, en_verbose = en_verbose)
                #model_trig, encoder_trig, his = fit_on_data(vec_trig, label_trig, model_trig, encoder_trig, the_lr, N_batch = N_batch, N_epoch = N_epoch, en_verbose = en_verbose)
                print('acc:{}, val_acc:{}'.format(his.history['acc'][-1], his.history['val_acc'][-1]))
                val_acc = test_on_data(model_trig, encoder_trig, X_test, Y_test, DIR_DATA, en_verbose = en_verbose)
                #val_acc = test_on_data(model_trig, encoder_trig, vec_trig, label_trig, DIR_DATA, en_verbose = en_verbose)
                joblib.dump([model_trig,encoder_trig], '{}_{:.5f}_{:.5f}_{:.5f}_{:.5f}.pkl'.format(
                    file_model_trig[0:-4], his.history['acc'][-1], val_acc, the_lr, N_batch)) # save the model to disk
                if val_acc > acc_pre:
                    acc_pre = val_acc
                    joblib.dump([model_trig,encoder_trig], '{}.pkl'.format(file_model_trig[0:-4])) # save the model to disk
                else:
                    break
DIR_DATAs = ['data_ACE_Chinese']#['data_test', 'data_military-corpus', 'data_ACE_English', 'data_ACE_Chinese', 'data_ACE']
for DIR_DATA in DIR_DATAs:
    training(DIR_DATA)

    





