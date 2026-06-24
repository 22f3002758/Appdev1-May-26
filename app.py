from flask import Flask
from backend.models import *
from flask_login import LoginManager

def create_app():
    app=Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///mydb.sqlite3"
    app.config["SECRET_KEY"]="mysecretkey"
    loginmanager=LoginManager(app)
    db.init_app(app)
    @loginmanager.user_loader
    def load_user(email):
        obj=db.session.query(Professional).filter_by(email=email).first() or db.session.query(Customer).filter_by(email=email).first() or db.session.query(Admin).filter_by(email=email).first()
        return obj
    app.app_context().push()
    
    return app

app=create_app()
from backend.routes import *
from backend.create_initial_data import *

if __name__=="__main__":
    app.run(debug=True)