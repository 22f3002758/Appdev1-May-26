from flask import Flask
from backend.models import *

def create_app():
    app=Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///mydb.sqlite3"
    db.init_app(app)
    app.app_context().push()
    
    return app

app=create_app()
from backend.routes import *
from backend.create_initial_data import *


# if db.session.query(Services).count()==0:
#     serv1=Services(name="Home Cleaning", baseprice=500)
#     serv2=Services(name="Home decor", baseprice=500)
#     db.session.add_all([serv1,serv2])
#     db.session.commit()

# if db.session.query(ServiceProvider).count()==0:
#     sp1=ServiceProvider(email="sp1@gmail.com", password='asdf',serviceid=1)
#     sp2=ServiceProvider(email="sp2@gmail.com", password='asdf',serviceid=1)
#     sp3=ServiceProvider(email="sp3@gmail.com", password='asdf',serviceid=2)
#     sp4=ServiceProvider(email="sp4@gmail.com", password='asdf',serviceid=2)
#     db.session.add_all([sp1,sp2,sp3,sp4])
#     db.session.commit()    

# serviceobj=db.session.query(Services).filter_by(id=1).first()  
# # print(serviceobj)  
# # print(serviceobj.name)
# # print(serviceobj.baseprice) 

# sp_obj=db.session.query(ServiceProvider).filter_by(id=1).first()
# print(sp_obj) 
# print(sp_obj.service.name)  

if __name__=="__main__":
    app.run(debug=True)