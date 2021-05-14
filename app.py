from flask import Flask,request
from flask_restful import Api, Resource, reqparse
#from .models import db, TableModel,Accepted_entries,Master_entries
import datetime
import json
from flask.cli import with_appcontext
import click
from flask_sqlalchemy import SQLAlchemy

 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] ="postgresql://xplore_phoenix_writer:write2phoenix@172.19.0.64:5432/phoenix_clone3"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_BINDS'] = {
    'local': 'postgresql://postgres:pooja5@PK@localhost:5432/API_DB',
    'master': 'postgresql://postgres:pooja5@PK@localhost:5432/API_DB'
}


db = SQLAlchemy()
 
class TableModel(db.Model):
    __table_args__ = {'schema': 'settings'}
    __tablename__ = 'user_acceptance'
    
    app_id = db.Column(db.String(80),primary_key=True)
    user_id = db.Column(db.String(80),primary_key=True)
    version=db.Column(db.Integer,primary_key=True)
    tstamp=db.Column(db.DateTime,primary_key=True)
    action=db.Column(db.String(80))
 
    def __init__(self,app_id,user_id,version,tstamp,action):
        self.app_id = app_id      #to remove for (auto-increment)
        self.user_id =user_id
        self.version=version
        self.tstamp=tstamp
        self.action=action
     
    def json1(self):
        return {"app_id":self.app_id, "user_id":self.user_id, "version":self.version  ,"tstamp":str(self.tstamp), "action":self.action}


class Accepted_entries(db.Model):
    __bind_key__ = "local"
    __table_args__ = {'schema': 'public'}
    __tablename__ = 'user_acceptance_accepted_entries'
    int_id = db.Column(db.Integer, primary_key=True)
    int_user_id = db.Column(db.Integer, nullable=False)
    txt_action_type = db.Column(db.Text, nullable=False)
    app_id = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.String(255), nullable=False)
    version = db.Column(db.Integer, nullable=False)
    tstamp = db.Column(db.DateTime, nullable=False)
    action = db.Column(db.String(255), nullable=False)
    def __init__(self, int_user_id, txt_action_type, app_id, user_id, version, tstamp, action):
        self.int_user_id = int_user_id
        self.txt_action_type = txt_action_type
        self.app_id = app_id
        self.user_id = user_id
        self.version = version
        self.tstamp = tstamp
        self.action = action
    def json1(self):
        return {"int_user_id":self.int_user_id,"txt_action_type":self.txt_action_type,"app_id":self.app_id, "user_id":self.user_id, "version":self.version, 
                "tstamp":str(self.tstamp), "action":self.action}

class Master_entries(db.Model):
    __bind_key__ = "master"
    __table_args__ = {'schema': 'public'}
    __tablename__ = 'master_user'
    int_user_id = db.Column(db.Integer, primary_key=True)
    user_name= db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean, nullable=False)
    def __init__(self,user_name,active):
        self.user_name=user_name
        self.active=active
    
    def json2(self):
        return {"int_user_id":self.int_user_id,"user_name":self.user_name, "active":self.active}

    
api = Api(app)
db.init_app(app)



def action_check(action):
    if(action=="viewed"):
        return(action)
    elif(action=="accepted"):
        return(action)
    elif(action=="declined"):
        return(action)
    else:
        return False

#Retrieves all the records and action specified records
@app.route('/records/')    
def allrecords():
    user_id=request.args.get('user_id')
    action=request.args.get('action')
    #if action & user_id is not given,it will return all the records from the db
    if(action==None and user_id==None):
        stores = TableModel.query.all()
        return {'user_acceptance':list(x.json1() for x in stores)} 

    if(action!=None and user_id!=None):
        return{'Message':'Query parameter(User_id) not allowed'},404

    #if action is given,it will return all the records based on the action specified
    if(action!=None):
        action=action_check(action)
        if action==False:
            return{"message":"No such action found"},404
        stores = TableModel.query.filter_by(action=action)
        return {'Result':list(x.json1() for x in stores)}
    else:
        return{'Message':'The url supports only action parameter'},400

#Retrieves single user details with/without action specified
@app.route('/record',methods=['GET'])    
def accepted_records():
    if request.args:
        user_id=request.args.get('user_id')
        action=request.args.get('action')
        #if action & user_id is given,it will return all the records of the user with the specified action
        if(action!=None and user_id!=None):
            #store_user holds the record of the user_id
            store_user = TableModel.query.filter_by(user_id=user_id)
            #action_check is a function that checks action is valid or not 
            action=action_check(action)
            #if action does not match with the values in the db,it will return false
            if action==False:
                return{"message":"No such action found"},404
            #converting the records stored in store_user to a list
            empty_record = list(x.json1() for x in store_user)
            #checking if the list is empty ie if the list is empty, no such user exist in the database
            if empty_record == []:
                return {"Message ": "No such user found"},400
            #store holds the record of the user_id based on the action
            store = TableModel.query.filter_by(user_id=user_id, action=action)
            if store:
                #converting the records stored in store to a list
                record_with_action = list(x.json1() for x in store)
                empty_list = [[],None]
                if record_with_action  in empty_list:
                    return{'Message':'Record not found with such action'},404
            # else:
                return {'user_acceptance':list(x.json1() for x in store)}
        else:
            #if only action is given in the url
            if(action!=None):
                action=action_check(action)
                if action==False:
                    return{"message":"No such action found"},404
                stores = TableModel.query.filter_by(action=action)
                
                record_with_action = list(x.json1() for x in stores)
                if record_with_action == []:
                    return {"Message ": "Invalid action ; kindly refer the doc"},404
                return {'user_acceptance':list(x.json1() for x in stores)}
            else:
                #if only user_id is given in the url without action
                stores = TableModel.query.filter_by(user_id=user_id)
                if stores:
                    record_with_action = list(x.json1() for x in stores)
                    if record_with_action == []:
                        return {"Message ": "No records found with such action"},404
                    return {'user_acceptance':list(x.json1() for x in stores)}
    return {"Message ": "Query parameter(s) missing . Query parameter(s) allowed : user_id , action or user_id&action"},400

#Retrieves the details of only specific users.
@app.route('/allrecords',methods=['GET']) 
def get_all_records():
    data = request.get_json()
    if data == None:
        return {'Message ': "Request body cannot be empty"}, 403
    if not request.json :
        return {"Message ": "Unsupported format"}, 400
    action = request.args.get('action')
    #if the users specify the action in the url, the below code will execute
    if action!=None:
        #action_check is a function that checks action is valid or not 
        action=action_check(action)
        #if action does not match with the values in the db,it will return false
        if action==False:
            return{"message":"No such action found"},404
        data = request.get_json()
        i=1
        dictionary={}           #stores the user id details 
        dictionary1={}          #stores the user id details wth action 
        result={}               #stores the final dictionary     
        dict_userIDs = data[0]   #stores the data from the body given by the end user
        for j in range(0,len(dict_userIDs['user_id'])): 
            store_user = TableModel.query.filter_by(user_id=dict_userIDs['user_id'][j])
            #values stored in store_user will be converted to dictionary format 
            dictionary={dict_userIDs['user_id'][j]:list(x.json1() for x in store_user)}
            #dictionary1.update(result)
            for key in dictionary:
                #checking if the dictionary value is empty ie record does not exist if the value is empty
                if ((dictionary[key])==[]):
                    dictionary[key]="Record does not exist"
                    result.update(dictionary)     #updating the final dictionary that will be displayed to the user
                else:
                    #if dictionary is not empty means that the user is registered in the db
                    #this else loop filters the user's record based on the action provided
                    #store variable holds the details of the user based on the action
                    store = TableModel.query.filter_by(user_id=dict_userIDs['user_id'][j],action=action)
                    #values stored in store will be converted to dictionary format  
                    dictionary1={dict_userIDs['user_id'][j]:list(x.json1() for x in store)}
                    for key in dictionary1:
                        if ((dictionary1[key])==[]):
                            dictionary1[key]="No record found with such action"
                            result.update(dictionary1) 
                        else:
                            result.update(dictionary1)                       
            i+=1
        return result
    else:
        #if action is not specified in the url
        data = request.get_json()
        i=1
        dictionary={}
        dictionary1={}
        dict_userIDs = data[0]
        for j in range(0,len(dict_userIDs['user_id'])):
        #for _ in range(len(data)):
            #body="{}".format(i)
            result={}
            store = TableModel.query.filter_by(user_id=dict_userIDs['user_id'][j])
            dictionary={dict_userIDs['user_id'][j]:list(x.json1() for x in store)}
            dictionary1.update(dictionary)
            for key in dictionary1:
                if (dictionary1[key])==[]:
                    dictionary1[key]="Record does not exist"
                    result.update(dictionary1) 
                else:
                    result.update(dictionary1)  
            i+=1
        return result

#single/multiple insert
@app.route('/records', methods=['POST'])
def post():
    if request.args:
        return {"Message ":"Unsupported Action ; query parameters are not allowed"},403
    data = request.get_json()
    if data == None:
        return {'Message ': "Request body cannot be empty"}, 403
    elif not request.json :
        return {"Message ": "Unsupported format"}, 400
    else:
        #taking the current dat and time
        tstamp = datetime.datetime.now()
        #if authorized by is not given by the user, an message will be displayed
        if 'authorized_by' not in data[1]:
            return {"Message ": "Please provide the key 'authorized_by' and your mail id as its value"},500
        #storing authorized_by
        auth_by = data[1]['authorized_by'] 
        #checking if the person is authorized to make an entry from the Master table
        record_user_id = Master_entries.query.filter_by(user_name = auth_by).first()
        if record_user_id == None:
            return {"Message " : "You are not authorized to make an entry!! Please contact Sree Harsha Chintamani"},401
        master_user_dict = record_user_id.json2()
        int_userID = master_user_dict['int_user_id']
        active_status = master_user_dict['active']
        dict_userIDs = data[0]   
        for j in range(0,len(dict_userIDs['user_id'])): 
            if active_status == False:
                return {"Message " : "You are only authorized to read an entry!! Please contact Sree Harsha Chintamani"},401
            new_record = TableModel('phoenix_windxplore', dict_userIDs['user_id'][j],'1', tstamp,'accepted')
            new_record1 = Accepted_entries(int_userID,'insert', "phoenix_windxplore", dict_userIDs['user_id'][j],'1', tstamp,'accepted')
            db.session.add(new_record)
            try :
                db.session.commit()
            except :
                return {"Message ": "Could not update in the Database!"}, 500
            db.session.add(new_record1)
            try :
                db.session.commit()
            except :
                return {"Message ": "Could not update in the local Database!"},500
        return {"Message " : "New record(s) added successfully"}, 200

#single/multiple delete
@app.route('/records',methods=['DELETE'])
def delete():
    data = request.get_json()
    if data == None:
        return {'Message ': "Request body cannot be empty"}, 403
    if not request.json :
        return {"Message ": "Unsupported format"}, 400
    if request.args :
        if "action" in request.args.keys():
            action = request.args.get('action')
            data = request.get_json()
            i=1
            dictionary={}
            dictionary1={}
            check_user={}
            if 'authorized_by' not in data[1]:
                return {"Message ": "Please provide the key 'authorized_by' and your mail id as its value"},500
            auth_by = data[1]['authorized_by'] 
            record_user_id = Master_entries.query.filter_by(user_name = auth_by).first()
            if record_user_id == None:
                return {"Message " : "You are not authorized to delete an entry!! Please contact Sree Harsha Chintamani"},401
            master_user_dict = record_user_id.json2()
            int_userID = master_user_dict['int_user_id']
            active_status = master_user_dict['active']
            dict_userIDs = data[0]
            for j in range(0,len(dict_userIDs['user_id'])): 
                if active_status == False:
                    return {"Message " : "You are only authorized to read an entry!! Please contact Sree Harsha Chintamani"},401

            # get records from main db
                store = TableModel.query.filter_by(user_id=dict_userIDs['user_id'][j],action=action)
                dictionary={i:list(x.json1() for x in store)}
                dictionary1.update(dictionary)
                check= list(dictionary1.values())[0]
                if check:
                    d={dict_userIDs['user_id'][j]:"Record not found"}
                    check_user.update(d)
                i+=1
            
            
          # insert records (those which would be deleted from main db) to local db
            for j in range(0,len(dict_userIDs['user_id'])):
                k=0
                store = Master_entries.query.filter_by(user_name=auth_by)
                dictionary={i:list(x.json2() for x in store)}
                first_value= list(dictionary.values())[0]
                if not first_value:
                    return{'message':'You are not authorized to delete an entry!! Please contact Sree Harsha Chintamani'},404    
                n=(first_value[0]['int_user_id'])
                active_value=(first_value[0]['active'])
                if(active_value==True):
                    str=datetime.datetime.now()
                    for j in dictionary1.values():
                        for p in j:
                            list1= list(p.values())
                            new_record = Accepted_entries(n,'delete',list1[0],list1[1],list1[2],str,list1[4])    
                            db.session.add(new_record)
                            try :
                                db.session.commit()
                            except:
                                abort(500, description={"Message ": f"Record {p} could be saved to local database"})
                            k+=1
                else:
                    return{'message':'You are only authorized to view an entry!!'}
            # delete from main db
            for j in range(0,len(dict_userIDs['user_id'])):
            #for j in range(len(data)):    
                record = TableModel.query.filter_by(user_id=dict_userIDs['user_id'][j],action=action).all()
                if record:
                    for i in record :
                        e={dict_userIDs['user_id'][j]:"Record deleted"}
                        check_user.update(e)
                        db.session.delete(i)
                        print("Inside delete loop")
                        print(check_user)
                        try :
                            db.session.commit()
                        except :
                            abort(500, description={"Message ":f"Record {i} could not be deleted from the database"})
                    
            return check_user
    else:
        data = request.get_json()
        i=1
        dictionary={}
        dictionary1={}
        check_user={}
        if 'authorized_by' not in data[1]:
            return {"Message ": "Please provide the key 'authorized_by' and your mail id as its value"},500
        auth_by = data[1]['authorized_by'] 
        record_user_id = Master_entries.query.filter_by(user_name = auth_by).first()
        if record_user_id == None:
            return {"Message " : "You are not authorized to delete an entry!! Please contact Sree Harsha Chintamani"},401
        master_user_dict = record_user_id.json2()
        int_userID = master_user_dict['int_user_id']
        active_status = master_user_dict['active']
        dict_userIDs = data[0]
        for j in range(0,len(dict_userIDs['user_id'])): 
            if active_status == False:
                return {"Message " : "You are only authorized to read an entry!! Please contact Sree Harsha Chintamani"},401

        # get records from main db
            store = TableModel.query.filter_by(user_id=dict_userIDs['user_id'][j])
            dictionary={i:list(x.json1() for x in store)}
            dictionary1.update(dictionary)
            check= list(dictionary1.values())[0]
            if check:
                d={dict_userIDs['user_id'][j]:"Record not found"}
                check_user.update(d)
            i+=1
        
        
        # insert records (those which would be deleted from main db) to local db
        for j in range(0,len(dict_userIDs['user_id'])):
            k=0
            store = Master_entries.query.filter_by(user_name=auth_by)
            dictionary={i:list(x.json2() for x in store)}
            first_value= list(dictionary.values())[0]
            if not first_value:
                return{'message':'You are not authorized to delete an entry!! Please contact Sree Harsha Chintamani'},404    
            n=(first_value[0]['int_user_id'])
            active_value=(first_value[0]['active'])
            if(active_value==True):
                str=datetime.datetime.now()
                for j in dictionary1.values():
                    for p in j:
                        list1= list(p.values())
                        new_record = Accepted_entries(n,'delete',list1[0],list1[1],list1[2],str,list1[4])    
                        db.session.add(new_record)
                        try :
                            db.session.commit()
                        except:
                            abort(500, description={"Message ": f"Record {p} could be saved to local database"})
                        k+=1
            else:
                return{'message':'You are only authorized to view an entry!!'}
        # delete from main db
        for j in range(0,len(dict_userIDs['user_id'])):
        #for j in range(len(data)):    
            record = TableModel.query.filter_by(user_id=dict_userIDs['user_id'][j]).all()
            if record:
                for i in record :
                    e={dict_userIDs['user_id'][j]:"Record deleted"}
                    check_user.update(e)
                    db.session.delete(i)
                    print("Inside delete loop")
                    print(check_user)
                    try :
                        db.session.commit()
                    except :
                        abort(500, description={"Message ":f"Record {i} could not be deleted from the database"})
                
        return check_user





@app.route('/')
def index():
    return "<h1>Welcome !!</h1>"

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)