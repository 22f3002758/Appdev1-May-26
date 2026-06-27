from flask import current_app as app
from flask import render_template, redirect,request
from .models import *
from datetime import datetime
from flask_login import login_user,login_required,current_user,logout_user

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
            newcust=Customer(name=fname,email=femail,password=fpwd,address=faddress,mobile=fmobile,status='Active')
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
            newprof=Professional(name=fname,email=femail,password=fpwd,address=faddress,mobile=fmobile,experience=fexp,status='Registered',resume_url="#")
            db.session.add(newprof)
            db.session.commit()
        return redirect("/login")
    

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=="GET":
        return render_template("login.html")
    if request.method=="POST":
        femail=request.form.get("email")
        fpwd=request.form.get("pwd")
        user=db.session.query(Professional).filter_by(email=femail).first() or \
        db.session.query(Customer).filter_by(email=femail).first() or\
        db.session.query(Admin).filter_by(email=femail).first() 
        if user:
            if user.password==fpwd:
                if isinstance(user,Professional):
                    login_user(user)
                    return redirect("professional/dashboard")
                elif isinstance(user,Customer):
                    login_user(user)
                    return redirect("customer/dashboard")
                elif isinstance(user,Admin):
                    login_user(user)
                    return redirect("admin/dashboard")
            else:
                return "Check your credentials"
        else:
            return "User not found"    
                
    
@app.route('/admin/dashboard', methods=['GET','POST'])
@login_required
def admin_dashboard():
    profs=db.session.query(Professional).all()
    customers=db.session.query(Customer).all()
    return render_template("admin/dashboard.html", profs=profs, customers=customers)

@app.route("/admin/professional/<string:action>/<int:prof_id>")
def approve_professional(action,prof_id):
    prof=db.session.query(Professional).filter_by(id=prof_id).first()
    if prof:
        if action=="Accept" and prof.status=="Registered":
            prof.status='Active'
            db.session.commit()
        elif action=="Reject" and prof.status=="Registered":
            prof.status='Rejected'
            db.session.commit()
        elif action=="Flag" and prof.status=="Active":
            prof.status='Flagged'
            for package in prof.packages:
                package.status="Inactive"
            db.session.commit()
        elif action=="Unflag" and prof.status=="Flagged":
            prof.status='Active'
            for package in prof.packages:
                package.status="Active"
            db.session.commit() 
        else:
            return "Invalid action or status"
    else:
        return "Professional not found."  
    return redirect("/admin/dashboard")   

@app.route("/admin/customer/<string:action>/<int:cust_id>")
def approve_customer(action,cust_id):
    cust=db.session.query(Customer).filter_by(id=cust_id).first()   
    if cust:
        if action=='Flag' and cust.status=='Active':
            cust.status='Flagged'
            db.session.commit()
        elif action=="Unflag" and cust.status=='Flagged':
            cust.status='Active'
            db.session.commit()
        else:  
            return "Invalid action or status"   
    else:
        return "Professional not found."  
    return redirect("/admin/dashboard")      


@app.route('/customer/dashboard', methods=['GET','POST'])
@login_required
def cust_dashboard():
    packs=db.session.query(Package).filter_by(status="Active").all()
    packages=[]
    for pack in packs:
        if pack.start_date<=datetime.now().date()<=pack.end_date:
            packages.append(pack)

    bookings=current_user.bookings
    return render_template("customer/dashboard.html",packages=packages, bookings=bookings)

@app.route('/customer/book/<int:pack_id>', methods=['GET','POST'])
@login_required
def book_package(pack_id):
     pack=db.session.query(Package).filter_by(id=pack_id).first()
     date=request.form.get("date")
     time=request.form.get("time")
     if pack and pack.status=='Active':
        if pack.start_date<=datetime.strptime(date,"%Y-%m-%d").date()<=pack.end_date:
            new_booking=Booking(cust_id=current_user.id,pack_id=pack.id,prof_id=pack.prof_id,status="Requested",date=datetime.strptime(date,"%Y-%m-%d").date(),
                                start_time=datetime.strptime(time,"%H:%M").time(),total_price=0)
            db.session.add(new_booking)
            db.session.commit()
        return redirect("/customer/dashboard")
     else:
         return "Package not available. "    


@app.route('/professional/dashboard', methods=['GET','POST'])
@login_required
def prof_dashboard():
    packages=db.session.query(Package).filter_by(prof_id=current_user.id).all()
    bookings=current_user.bookings
    return render_template("professional/dashboard.html",packages=packages, bookings=bookings)  

@app.route('/professional/add_package', methods=['GET','POST'])
@login_required
def add_pack():
    title=request.form.get("title")
    description=request.form.get("description")
    price=request.form.get("price")
    start_date=datetime.strptime(request.form.get("start_date"),"%Y-%m-%d").date()
    end_date=datetime.strptime(request.form.get("end_date"),"%Y-%m-%d").date()
    pack=db.session.query(Package).filter_by(title=title).first()
    if pack:
        return "Package already exist"
    else:
        newpack=Package(title=title, description=description,price=price,start_date=start_date,end_date=end_date,prof_id=current_user.id,status="Active")
        db.session.add(newpack)
        db.session.commit()
        return redirect("/professional/dashboard")
    
@app.route('/professional/edit_package/<int:pack_id>', methods=['GET','POST'])
@login_required
def edit_pack(pack_id):
    title=request.form.get("title")
    description=request.form.get("description")
    price=request.form.get("price")
    start_date=datetime.strptime(request.form.get("start_date"),"%Y-%m-%d").date()
    end_date=datetime.strptime(request.form.get("end_date"),"%Y-%m-%d").date()
    pack=db.session.query(Package).filter_by(id=pack_id).first()
    if title:
        pack.title=title
    if description:
        pack.description=description   
    if price:
        pack.price=price
    if start_date:
        pack.start_date=start_date
    if end_date:
        pack.end_date=end_date
        db.session.commit()
        return redirect("/professional/dashboard")    
    
@app.route('/professional/delete/<int:pack_id>', methods=['GET','POST'])
@login_required
def delete_pack(pack_id):
    pack=db.session.query(Package).filter_by(id=pack_id).first()
    if pack:
        db.session.delete(pack)
        db.session.commit()
        return redirect("/professional/dashboard")  

@app.route('/professional/<string:action>/<int:booking_id>', methods=['GET','POST'])
@login_required
def Prof_booking(action,booking_id):
    booking=db.session.query(Booking).filter_by(id=booking_id).first() 
    if booking:
        if action=="Accept" and booking.status=="Requested":
            booking.status="Accepted"
        elif action=="Reject" and booking.status=="Requested":
            booking.status="Rejected"
        db.session.commit()
    return redirect("/professional/dashboard")  

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")
    
