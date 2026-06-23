from flask import current_app as app
from flask import render_template, redirect,request
from backend.models import *
from datetime import datetime

@app.route('/')
def home():
    return render_template("home.html")

@app.route("/register",methods=["GET","POST"])
def register():
    if request.args.get("role")=='customer' and request.method=='GET':
        return render_template('customer/register.html')
    if request.args.get("role")=='professional' and request.method=='GET':
        return render_template('professional/register.html')
    elif request.method=='POST' and request.args.get("role")=='customer':
        fname=request.form.get("cust_name")
        femail=request.form.get("cust_email")
        fpwd=request.form.get("cust_pwd")
        faddress=request.form.get("cust_address")
        fmobile=request.form.get("cust_mobile")
        cust=db.session.query(Customer).filter_by(email=femail).first()
        if cust:
            return "Customer already exist!"
        else:
            newcust=Customer(name=fname,email=femail,password=fpwd,address=faddress,mobile=fmobile,status='active')
            db.session.add(newcust)
            db.session.commit()
        return redirect("/login")
    elif request.method=='POST' and request.args.get("role")=='professional':
        fname=request.form.get("p_name")
        femail=request.form.get("p_email")
        fpwd=request.form.get("p_pwd")
        faddress=request.form.get("p_address")
        fmobile=request.form.get("p_mobile")
        fexp=request.form.get("p_exp")
        resume=request.files.get("resume")
        prof=db.session.query(Professional).filter_by(email=femail).first()
        if prof:
            return "Professional already exist!"
        else:
            # resume.save(f"static/{email}.pdf")
            newprof=Professional(name=fname,email=femail,password=fpwd,address=faddress,mobile=fmobile,experience=fexp,status='pending',resume_url="#")
            db.session.add(newprof)
            db.session.commit()
        return redirect("/login")
    

@app.route('/')
def login():
    return render_template("login.html")      