import pandas as pd
import numpy as np
import string
import re
import os
import sys
import functools
import math
import json

def evaluate_expression(expression,data):
    """
    Return the value computed using given expression over data.
    """
    operators=['+','-','*','/','exp','exp-','^-1','^2','^3','sqrt','cbrt','log','abs','^6','sin','cos','(',')']
    OPTR=[]
    OPND=[]
    s=''
    i=0
    while i < len(expression):
        if re.match(r'\w',expression[i]):
            s+=expression[i]
        elif expression[i]=='-' and expression[i-1]=='p':
            s+=expression[i]
        else:
            if s:
                if s in operators:
                    OPTR.append(s)
                else:
                    OPND.append(data[s])
                s=''
            OPTR.append(expression[i])
            if expression[i]==')':
                OPTR.pop()
                if i+1<len(expression) and expression[i+1]=='^':
                    pattern=re.compile(r'\^-?\d')
                    power=pattern.match(expression,i+1).group()
                    i+=len(power)
                    operand=OPND.pop()
                    if power=='^-1':
                        OPND.append(np.power(operand,-1))
                    elif power=='^2':
                        OPND.append(np.power(operand,2))
                    elif power=='^3':
                        OPND.append(np.power(operand,3))
                    elif power=='^6':
                        OPND.append(np.power(operand,6))
                    OPTR.pop()
                elif len(OPTR)>1 and OPTR[-1]=='(':
                    operand=OPND.pop()
                    if OPTR[-2]=='exp':
                        OPND.append(np.exp(operand))
                    elif OPTR[-2]=='exp-':
                        OPND.append(np.exp(-operand))
                    elif OPTR[-2]=='sqrt':
                        OPND.append(np.sqrt(operand))
                    elif OPTR[-2]=='cbrt':
                        OPND.append(np.cbrt(operand))
                    elif OPTR[-2]=='log':
                        OPND.append(np.log(operand))
                    elif OPTR[-2]=='abs':
                        OPND.append(np.abs(operand))
                    elif OPTR[-2]=='sin':
                        OPND.append(np.sin(operand))
                    elif OPTR[-2]=='cos':
                        OPND.append(np.cos(operand))
                    OPTR.pop()
                    OPTR.pop()
                elif len(OPTR)==1 and OPTR[0]=='(':
                    pass
                else:
                    operand2=OPND.pop()
                    operand1=OPND.pop()
                    operator=OPTR.pop()
                    OPTR.pop()
                    if operator=='+':
                        OPND.append(operand1+operand2)
                    elif operator=='-':
                        if OPTR[-1]=='abs':
                            OPND.append(np.abs(operand1-operand2))
                            OPTR.pop()
                        else:
                            OPND.append(operand1-operand2)
                    elif operator=='*':
                        OPND.append(operand1*operand2)
                    elif operator=='/':
                        OPND.append(operand1/operand2)
        i+=1
    return OPND.pop()


def compute_using_descriptors(path=None,result=None,training=True,data=None,task_idx=None,dimension_idx=None):
    """
    Return a list [task_index], whose item is numpy array [dimension, sample_index],
    whose item is the value computed using descriptors found by SISSO.
    """
    if path:
        result=Result(path)
    pred=[]
    if training==True:
        for task in range(0,result.task_number):
            pred_t=[]
            for dimension in range(0,result.dimension):
                value=0
                for i in range(0,dimension+1):
                    value+=result.coefficients()[task][dimension][i]*evaluate_expression(result.descriptors()[dimension][i],result.data_task[task])
                value+=result.intercepts()[task][dimension]
                pred_t.append(list(value))
            pred.append(np.array(pred_t))
    if training==False:
        if data==None:
            for task in range(0,result.task_number):
                pred_t=[]
                for dimension in range(0,result.dimension):
                    value=0
                    for i in range(0,dimension+1):
                        value+=result.coefficients()[task][dimension][i]*evaluate_expression(result.descriptors()[dimension][i],result.validation_data_task[task])
                    value+=result.intercepts()[task][dimension]
                    pred_t.append(list(value))
                pred.append(np.array(pred_t))
        else:
            if isinstance(data,str):
                data=pd.read_csv(os.path.join(data),sep=' ')
            else:
                for i in range(0,dimension_idx):
                    value+=result.coefficients()[task_idx][dimension_idx][i]*evaluate_expression(result.descriptors()[dimension_idx][i],data)
                value+=result.intercepts()[task_idx][dimension_idx]
                pred=value
    return pred

'''
def errors(result=None,training=True):
    """
    Return the errors of given class Result's data or a given data path.
    """
    """
    if path:
        result=Result(path)
    if data_path:
        data=pd.read_csv(data_path,sep=' ')
    else:
        data=result.data
    samples_num=len(data)
    property_test=data.iloc[:,1]
    error=np.zeros(shape=(result.dimension,6))
    for dimension in range(0,result.dimension):
        value=0
        for i in range(0,dimension+1):
            value+=result.coefficients()[dimension][i]*evaluate_expression(result.descriptors()[dimension][i],data)
        value+=result.intercepts()[dimension]
        sorted_error=np.sort(np.abs(value-property_test))
        error[dimension]=np.array([np.sqrt(np.mean(np.power(sorted_error,2))),
                            np.mean(sorted_error),
                            sorted_error[math.ceil(samples_num*0.5)-1],
                            sorted_error[math.ceil(samples_num*0.75)-1],
                            sorted_error[math.ceil(samples_num*0.95)-1],
                            sorted_error[-1]])
    error=pd.DataFrame(error,columns=['RMSE','MAE','50%ile AE','75%ile AE','95%ile AE','MaxAE'],index=list(range(1,result.dimension+1)))
    return error
    """
    if training=True:
        items_error=result.training_values()-result.property.values
'''

'''
def item_errors(result=None,*item_index):
    """
    Return the errors of item_index data point in the data set.
    """
    
    if path:
        result=Result(path)
    if data_path:
        data=pd.read_csv(data_path,sep=' ')
    else:
        data=result.data
    data=data.iloc[item_index]
    property_test=data.iloc[1]
    error=np.zeros(result.dimension)
    for dimension in range(0,result.dimension):
        value=0
        for i in range(0,dimension+1):
            value+=result.coefficients()[dimension][i]*evaluate_expression(result.descriptors()[dimension][i],data)
        value+=result.intercepts()[dimension]
        error[dimension]=value-property_test
    return error
'''

def compute_errors(errors):
    """
    Return the errors of given numpy array errors (task_index, dimension, sample_index), if errors is 2D numpy array,
    or return the errors of given 1D numpy array error
    """
    
    if isinstance(errors[0],float):
        error=np.zeros(shape=(1,6))
        samples_num=len(errors)
        sorted_error=np.sort(np.abs(errors))
        error[0]=np.array([np.sqrt(np.mean(np.power(sorted_error,2))),
                                np.mean(sorted_error),
                                sorted_error[math.ceil(samples_num*0.5)-1],
                                sorted_error[math.ceil(samples_num*0.75)-1],
                                sorted_error[math.ceil(samples_num*0.95)-1],
                                sorted_error[-1]])
        error=pd.DataFrame(error,columns=['RMSE','MAE','50%ile AE','75%ile AE','95%ile AE','MaxAE'])
    elif isinstance(errors,list) and isinstance(errors[0],np.ndarray):
        task_num=len(errors)
        dimension_num=len(errors[0])
        error=[]
        for task in range(0,task_num):
            error_t=np.zeros(shape=(dimension_num,6))
            samples_num=errors[task].shape[1]
            for dimension in range(0,dimension_num):
                sorted_error=np.sort(np.abs(errors[task][dimension]))
                error_t[dimension]=np.array([np.sqrt(np.mean(np.power(sorted_error,2))),
                                    np.mean(sorted_error),
                                    sorted_error[math.ceil(samples_num*0.5)-1],
                                    sorted_error[math.ceil(samples_num*0.75)-1],
                                    sorted_error[math.ceil(samples_num*0.95)-1],
                                    sorted_error[-1]])
            error.append(pd.DataFrame(error_t,columns=['RMSE','MAE','50%ile AE','75%ile AE','95%ile AE','MaxAE'],index=list(range(1,dimension_num+1))))
    elif errors.ndim==2:
        samples_num=len(errors[0])
        dimensions=len(errors)
        error=np.zeros(shape=(dimensions,6))
        for dimension in range(0,dimensions):
            sorted_error=np.sort(np.abs(errors[dimension]))
            error[dimension]=np.array([np.sqrt(np.mean(np.power(sorted_error,2))),
                                np.mean(sorted_error),
                                sorted_error[math.ceil(samples_num*0.5)-1],
                                sorted_error[math.ceil(samples_num*0.75)-1],
                                sorted_error[math.ceil(samples_num*0.95)-1],
                                sorted_error[-1]])
        error=pd.DataFrame(error,columns=['RMSE','MAE','50%ile AE','75%ile AE','95%ile AE','MaxAE'],index=list(range(1,dimensions+1)))
    return error


class Result(object):
    """
    Evaluate the SISSO results.
    """
    def __init__(self,current_path):
        self.current_path=current_path
        with open(os.path.join(self.current_path,'SISSO.in'),'r') as f:
            input_file=f.read()
            subs_sis=int(re.findall(r'subs_sis\s*=\s*(\d+)',input_file)[0])
            rung=int(re.findall(r'rung\s*=\s*(\d+)',input_file)[0])
            dimension=int(re.findall(r'desc_dim\s*=\s*(\d+)',input_file)[0])
            operation_set=re.findall(r"opset\s*=\s*'(.+)'",input_file)
            operation_set=re.split(r'[\(\)]+',operation_set[0])[1:-1]
            task_number=int(re.findall(r'ntask\s*=\s*(\d+)',input_file)[0])
            samples_number=re.findall(r'nsample\s*=\s*([\d, ]+)',input_file)[0]
            samples_number=re.split(r'[,\s]+',samples_number)
            if samples_number[-1]=='':
                samples_number=samples_number[:-1]
            samples_number=list(map(int,samples_number))
            task_weighting=int(re.findall(r'task_weighting\s*=\s*(\d+)',input_file)[0])
        self.task_weighting=task_weighting
        self.task_number=task_number
        self.operation_set=operation_set
        self.subs_sis=subs_sis
        self.rung=rung
        self.dimension=dimension
        self.samples_number=samples_number
        self.data=pd.read_csv(os.path.join(current_path,'train.dat'),sep=' ')
        self.property_name=self.data.columns.tolist()[1]
        self.property=self.data.iloc[:,1]
        self.features_name=self.data.columns.tolist()[2:]
        self.materials=self.data.iloc[:,0]
        
        self.data_task=[]
        self.property_task=[]
        self.materials_task=[]
        i=0
        for task in range(0,self.task_number):
            self.data_task.append(self.data.iloc[i:i+self.samples_number[task]])
            self.property_task.append(self.property.iloc[i:i+self.samples_number[task]])
            self.materials_task.append(self.materials.iloc[i:i+self.samples_number[task]])
            i+=self.samples_number[task]
        
        if os.path.exists(os.path.join(self.current_path,'validation.dat')):
            self.validation_data=pd.read_csv(os.path.join(current_path,'validation.dat'),sep=' ')
            with open(os.path.join(self.current_path,'shuffle.dat'),'r') as f:
                shuffle=json.load(f)
            self.samples_number=shuffle['training_samples_number']
            self.validation_samples_number=shuffle['validation_samples_number']
            self.validation_data_task=[]
            i=0
            for task in range(0,self.task_number):
                self.validation_data_task.append(self.validation_data.iloc[i:i+self.validation_samples_number[task]])
                i+=self.validation_samples_number[task]

    
    def descriptors(self,path=None):
        """
        Return a list, whose ith item is ith D descriptors.
        """
        if path==None:
            path=self.current_path
        descriptors_all=[]
        with open(os.path.join(path,'SISSO.out'),'r') as f:
            input_file=f.read()
            descriptors_total=re.findall(r'descriptor:[\s\S]*?coefficients',input_file)
            for dimension in range(0,self.dimension):
                descriptors_d=descriptors_total[dimension]
                descriptors_d=re.split(r'\s+',descriptors_d)
                descriptors_d=descriptors_d[1:dimension+2]
                descriptors_d=[x[1] for x in list(map(lambda x: re.split(r':',x),descriptors_d))]
                descriptors_d=list(map(lambda x: x.replace(r'[',r'('),descriptors_d))
                descriptors_d=list(map(lambda x: x.replace(r']',r')'),descriptors_d))
                descriptors_all.append(descriptors_d)
        return descriptors_all
    
    def coefficients(self,path=None):
        """
        Return a list [task_index, dimension, descriptor_index]
        """
        if path==None:
            path=self.current_path
        coefficients_all=[]
        for task in range(0,self.task_number):
            coefficients_t=[]
            with open(os.path.join(path,'SISSO.out'),'r') as f:
                input_file=f.read()
                coefficients_total=re.findall(r'coefficients_00%d:(.*)'%(task+1),input_file)
                for dimension in range(0,self.dimension):
                    coefficients_d=re.split(r'\s+',coefficients_total[dimension])[1:]
                    coefficients_d=list(map(float,coefficients_d))
                    coefficients_t.append(coefficients_d)
            coefficients_all.append(coefficients_t)
        return coefficients_all
                
    
    def intercepts(self,path=None):
        """
        Return a list [task_index, dimension]
        """
        if path==None:
            path=self.current_path
        intercepts_all=[]
        for task in range(0,self.task_number):
            with open(os.path.join(path,'SISSO.out'),'r') as f:
                input_file=f.read()
                intercepts_t=re.findall(r'Intercept_00%d:(.*)'%(task+1),input_file)
                intercepts_t=list(map(float,intercepts_t))
            intercepts_all.append(intercepts_t)
        return intercepts_all
    
    def features_percent(self):
        """
        Compute the percentages of each feature in top subs_sis 1D descriptors.
        """
        """
        feature_space=pd.read_csv(os.path.join(self.current_path,'feature_space','Uspace.name'),sep=' ',header=None).iloc[0:self.subs_sis,0]
        feature_percent=pd.DataFrame(columns=('feature','percent'))
        index=0
        for feature_name in self.features_name:
            percent=feature_space.str.contains(feature_name).sum()/self.subs_sis
            feature_percent.loc[index]={'feature':feature_name,'percent':percent}
            index+=1
        feature_percent.sort_values('percent',inplace=True,ascending=False)
        return feature_percent
        """
        feature_space=pd.read_csv(os.path.join(self.current_path,'feature_space','Uspace.name'),sep=' ',header=None).iloc[0:self.subs_sis,0]
        feature_percent=pd.DataFrame(columns=self.features_name,index=('percent',))
        for feature_name in self.features_name:
            percent=feature_space.str.contains(feature_name).sum()/self.subs_sis
            feature_percent.loc['percent',feature_name]=percent
        return feature_percent
    
    def evaluate_expression(self,expression,data=None):
        """
        Return the value computed using given expression over data.
        """
        return evaluate_expression(expression,self.data)
    
    def values(self,training=True,display_task=False):
        """
        Return a 2D numpy array [dimension, sample_index],
        whose item is the value computed using descriptors found by SISSO.
        
        Return numpy array (task_index, sample_index, dimension),
        """
        if training==True:
            if display_task==True:
                return compute_using_descriptors(result=self)
            else:
                return np.hstack(compute_using_descriptors(result=self))
    
    def errors(self,training=True,display_task=False):
        """
        Return a numpy array [task, dimension, sample_index], whose value is error.
        
        Return a numpy array [dimension, sample_index], whose value is error.
        """
        if training==True:
            if display_task==True:
                pred=self.values(training=True,display_task=True)
                return [pred[task]-self.property_task[task].values for task in range(0,self.task_number)]
            else:
                return self.values(training=True,display_task=False)-self.property.values
    
    def total_errors(self,training=True,display_task=False):
        """
        Return a list [task_index], whose item is a pandas DataFrame [dimension, type of error]
        
        Return a pandas DataFrame [dimension, type of error].
        """
        return compute_errors(self.errors(training=True,display_task=display_task))




class Results(Result):
    """
    Evaluate the cross validation results of SISSO.
    """
    
    def __init__(self,current_path,property_name,cv_number):
        self.current_path=current_path
        self.property_name=property_name
        self.cv_number=cv_number
        
        with open(os.path.join(self.current_path,'%s_cv0'%(self.property_name),'SISSO.in'),'r') as f:
                input_file=f.read()
                subs_sis=int(re.findall(r'subs_sis\s*=\s*(\d+)',input_file)[0])
                rung=int(re.findall(r'rung\s*=\s*(\d+)',input_file)[0])
                dimension=int(re.findall(r'desc_dim\s*=\s*(\d+)',input_file)[0])
                operation_set=re.findall(r"opset\s*=\s*'(.+)'",input_file)
                operation_set=re.split(r'[\(\)]+',operation_set[0])[1:-1]
                task_number=int(re.findall(r'ntask\s*=\s*(\d+)',input_file)[0])
                task_weighting=int(re.findall(r'task_weighting\s*=\s*(\d+)',input_file)[0])
        self.task_number=task_number
        self.task_weighting=task_weighting
        self.operation_set=operation_set
        self.subs_sis=subs_sis
        self.rung=rung
        self.dimension=dimension
        self.total_materials_number=len(pd.read_csv(os.path.join(current_path,'train.dat'),sep=' '))
        self.data=[]
        self.materials=[]
        self.samples_number=[]
        self.validation_samples_number=[]
        self.property=[]
        self.validation_data=[]
        for cv in range(0,self.cv_number):
            self.data.append(pd.read_csv(os.path.join(current_path,'%s_cv%d'%(self.property_name,cv),'train.dat'),sep=' '))
            self.validation_data.append(pd.read_csv(os.path.join(current_path,'%s_cv%d'%(self.property_name,cv),'validation.dat'),sep=' '))
            self.property.append(pd.read_csv(os.path.join(current_path,'%s_cv%d'%(self.property_name,cv),'train.dat'),sep=' ').iloc[:,1])
            self.materials.append(self.data[cv].iloc[:,0])
            with open(os.path.join(self.current_path,'%s_cv0'%(self.property_name),'shuffle.dat'),'r') as f:
                shuffle=json.load(f)
            self.samples_number.append(shuffle['training_samples_number'])
            self.validation_samples_number.append(shuffle['validation_samples_number'])
        self.features_name=self.data[0].columns.tolist()[2:]
        self.samples_number=np.array(self.samples_number)
        self.validation_samples_number=np.array(self.validation_samples_number)
        
        self.data_task=[]
        self.property_task=[]
        self.materials_task=[]
        self.validation_data_task=[]
        for cv in range(0,self.cv_number):
            data_t=[]
            property_t=[]
            materials_t=[]
            validation_data_t=[]
            i,j=0,0
            for task in range(0,self.task_number):
                data_t.append(self.data[cv].iloc[i:i+self.samples_number[cv,task]])
                validation_data_t.append(self.validation_data[cv].iloc[j:j+self.validation_samples_number[cv,task]])
                property_t.append(self.property[cv].iloc[i:i+self.samples_number[cv,task]])
                materials_t.append(self.materials[cv].iloc[i:i+self.samples_number[cv,task]])
                i+=self.samples_number[cv,task]
                j+=self.validation_samples_number[cv,task]
            self.data_task.append(data_t)
            self.validation_data_task.append(validation_data_t)
            self.property_task.append(property_t)
            self.materials_task.append(materials_t)
        self.property_task=np.array(self.property_task)
        self.materials_task=np.array(self.materials_task)
    
    
    def find_materials_in_validation(self,*idxs):
        val_num=len(self.validation_data[0])
        return [self.validation_data[int(index/val_num)].iloc[index%val_num,0] for index in idxs]
    
    def descriptors(self):
        """
        Return a list whose index refers to the index of corss validation.
        Each item in the list is also a list, whose jth item is j+1 D descriptors.
        """
        return [super(Results,self).descriptors(path=os.path.join(self.current_path,'%s_cv%d'%(self.property_name,cv))) for cv in range(0,self.cv_number)]
    
    def coefficients(self):
        """
        Return a list whose index refers to the index of corss validation.
        Each item in the list is also a list, whose jth item is j+1 D coefficients.
        """
        return [super(Results,self).coefficients(path=os.path.join(self.current_path,'%s_cv%d'%(self.property_name,cv))) for cv in range(0,self.cv_number)]
    
    def intercepts(self):
        """
        Return a list whose index refers to the index of corss validation.
        Each item in the list is also a list, whose jth item is j+1 D intercepts.
        """
        return [super(Results,self).intercepts(path=os.path.join(self.current_path,'%s_cv%d'%(self.property_name,cv))) for cv in range(0,self.cv_number)]
    
    def features_percent(self):
        """
        Return the percent of each feature in the top subs_sis descriptors.
        There are total cv_number*subs_sis descriptors,
        the feature percent is the percent over these descriptors.
        """
        feature_percent=pd.DataFrame(columns=self.features_name,index=('percent',))
        feature_percent.iloc[0,:]=0
        for cv in range(0,self.cv_number):
            feature_space=pd.read_csv(os.path.join(self.current_path,'%s_cv%d'%(self.property_name,cv),'feature_space','Uspace.name'),sep=' ',header=None).iloc[0:self.subs_sis,0]
            for feature_name in self.features_name:
                count=feature_space.str.contains(feature_name).sum()
                feature_percent.loc['percent',feature_name]+=count
        feature_percent.iloc[0,:]=feature_percent.iloc[0,:]/(self.cv_number*self.subs_sis)
        return feature_percent
    
    def descriptor_percent(self,descriptor):
        """
        Return the percent of given descriptor appearing in the cross validation top subs_sis descriptors,
        and return the appearing index in the descriptor space.
        """
        count=0
        descriptor_index=np.zeros(self.cv_number)
        for cv in range(0,self.cv_number):
            feature_space=pd.read_csv(os.path.join(self.current_path,'%s_cv%d'%(self.property_name,cv),'feature_space','Uspace.name'),sep=' ',header=None).iloc[0:self.subs_sis,0]
            try:
                descriptor_index[cv]=feature_space.tolist().index(descriptor)+1
                count+=1
            except ValueError:
                descriptor_index[cv]=None
        return count/self.cv_number,descriptor_index
    
    def values(self,training=True,display_cv=False,display_task=False):
        """
        Return a list [cv_index],
        whose item is a list [task_index], whose item is a 2D numpy array [dimension, sample_index, dimension].
        
        Return a list [cv_index], whose item is a 2D numpy array [dimension, sample_index],
        whose item is the value computed using descriptors found by SISSO.
        """
        if display_cv==True:
            if training==True:
                if display_task==True:
                    return [compute_using_descriptors(path=os.path.join(self.current_path,'%s_cv%d'%(self.property_name,cv)))
                            for cv in range(0,self.cv_number)]
                else:
                    return [np.hstack(compute_using_descriptors(path=os.path.join(self.current_path,'%s_cv%d'%(self.property_name,cv))))
                    for cv in range(0,self.cv_number)]
            else:
                if display_task==True:
                    return [compute_using_descriptors(path=os.path.join(self.current_path,'%s_cv%d'%(self.property_name,cv)),
                                            training=False)
                    for cv in range(0,self.cv_number)]
                else:
                    return [np.hstack(compute_using_descriptors(path=os.path.join(self.current_path,'%s_cv%d'%(self.property_name,cv)),
                                            training=False))
                    for cv in range(0,self.cv_number)]
        else:
            return np.hstack(self.values(training=training,display_cv=True,display_task=False))
    
    def errors(self,training=True,display_cv=False,display_task=False):
        """
        Return a list [cv_index, task_index],
        whose item is a 2D numpy array [dimension, sample_index].
        
        Return a list [cv_index],
        whose item is a 2D numpy array [dimension, sample_index].
        """
        if display_cv==True:
            if training==True:
                if display_task==True:
                    error=[]
                    pred=self.values(training=True,display_cv=True,display_task=True)
                    for cv in range(0,self.cv_number):
                        error_cv=[]
                        for task in range(0,self.task_number):
                            error_cv.append(pred[cv][task]-self.property_task[cv][task].values)
                        error.append(error_cv)
                    return error
                else:
                    pred=self.values(training=True,display_cv=True,display_task=True)
                    return [np.hstack(pred[cv])-np.hstack(self.property_task[cv])
                            for cv in range(0,self.cv_number)]
            else:
                if display_task==True:
                    error=[]
                    pred=self.values(training=False,display_cv=True,display_task=True)
                    for cv in range(0,self.cv_number):
                        error_cv=[]
                        for task in range(0,self.task_number):
                            error_cv.append(pred[cv][task]-self.validation_data_task[cv][task].iloc[:,1].values)
                        error.append(error_cv)
                    return error
                else:
                    pred=self.values(training=False,display_cv=True,display_task=True)
                    return [(np.hstack(pred[cv])-self.validation_data[cv].iloc[:,1].values)
                            for cv in range(0,self.cv_number)]
        else:
            return np.hstack(self.errors(training=training,display_cv=True,display_task=False))
        
    def total_errors(self,training=True):
        """
        Return the errors over whole cross validation.
        """
        return compute_errors(self.errors(training=training,display_cv=False,display_task=False))