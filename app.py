
from flask import Flask,render_template,redirect,request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pickle
import pandas as pd
import numpy as np
import io
import csv
from flask import make_response
from io import StringIO

# <----------------------------LIBRARIES-------------------------------------->

app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///test.db"
app.config["SQLALCHEMY_DATABASE_URI"]="mysql+pymysql://root:qwerty@localhost/customer"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= False

db=SQLAlchemy(app)

def transform(text_file_contents):
    return text_file_contents.replace("=", ",")

class Customer(db.Model):
    srno = db.Column(db.Integer,primary_key=True)
    customer_id = db.Column(db.Integer,nullable=False)
    customer_name = db.Column(db.String(100),nullable=False)
    water_pumps = db.Column(db.Integer,nullable=False)
    water_pumps_id = db.Column(db.Integer,nullable=False)
    date_created = db.Column(db.DateTime,default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.srno}:{self.customer_id} {self.customer_name} {self.water_pumps}"



@app.route('/')
def hello():
    return render_template("index.html")


@app.route('/add_customer',methods=["GET","POST"])
def customer_form():
    if request.method == "POST":
        customer_id = request.form["customer_id"]
        customer_name = request.form["customer_name"]
        water_pumps = request.form["water_pumps"]
        water_pumps_id = request.form["water_pumps_id"]
        reg = Customer(customer_id=customer_id,customer_name=customer_name,water_pumps=water_pumps,water_pumps_id=water_pumps_id)
        db.session.add(reg)
        db.session.commit()
        return redirect("/customer_details")
    return render_template("add_customer.html")

@app.route("/customer_details")
def customer_table():
    get_all_customer = Customer().query.all()
    return render_template("customer_table.html",get_all_customer=get_all_customer)

@app.route("/update_customer/<int:sno>",methods=["GET","POST"])
def updation(sno):
    customer = Customer.query.filter_by(srno=sno).first()
    if request.method == "POST":
        customer.customer_id = request.form["customer_id"]
        customer.customer_name = request.form["customer_name"]
        customer.water_pumps_id = request.form["water_pumps_id"]
        customer.water_pumps = request.form["water_pumps"]
        db.session.commit()
        return redirect("/customer_details")
    return render_template("update_Customer.html",customer=customer,sno=sno)

@app.route("/delete_customer/<int:sno>")
def delete(sno):
    delete_customer = Customer().query.filter_by(srno=sno).first()
    db.session.delete(delete_customer)
    db.session.commit()
    return redirect("/customer_details")

@app.route("/upload",methods=["GET","POST"])
# def random_forest():
#     model = pickle.load(open("NewRFC.pkl",'rb'))
#     if request.method=="POST":
#         f = request.files['file']
#         f.save(f.filename)
#         test = pd.read_csv(f.filename)
#         pp = model.predict(test)
#         df = pd.DataFrame(pp)
#         file = df.to_csv("prediction.csv")
#         return redirect("Prediction_download.html",prediction=file)
#     return render_template("machine_learning.html")


def transform_view():
    f = request.files['data_file']
    if not f:
        return "No file"
    stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
    # csv_input = csv.reader(stream)
        #print("file contents: ", file_contents)
        #print(type(file_contents))
    # print(csv_input)
    # for row in csv_input:
            # print(row)

    stream.seek(0)
    result = transform(stream.read())

    df = pd.read_csv(StringIO(result))
        

        # load the model from disk
    loaded_model = pickle.load(open("NewRFC.pkl", 'rb'))
    df['prediction'] = loaded_model.predict(df)

        

    response = make_response(df.to_csv())
    response.headers["Content-Disposition"] = "attachment; filename=result.csv"
    return response

@app.route("/ml_model")
def form():
    return render_template("Prediction_download.html") 
    # """
    # {% extends 'base.html' %}

    # {% block base %}
    #     <h1>Let's TRY to Predict..</h1>
    #     </br>
    #     </br>
    #     <p> Insert your CSV file and then download the Result
    #     <form action="/upload" method="post" enctype="multipart/form-data">
    #         <input type="file" name="data_file" class="btn btn-block"/>
    #         </br>
    #         </br>
    #         <button type="submit" class="btn btn-primary btn-block btn-large">Predict</button>
    #     </form>
    
    # {% endblock base %}
    # """

if __name__ == "__main__":
    app.run(debug=True)