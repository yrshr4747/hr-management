from flask import Flask, render_template, flash, redirect, request, url_for, session, logging, jsonify, make_response
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, validators, SelectField,FileField
from flask_wtf.file import FileField
from passlib.hash import sha256_crypt
from functools import wraps
from datetime import date, timedelta
from werkzeug.utils import secure_filename
# from flask_reuploaded import UploadSet, configure_uploads, IMAGES
# import pdfkit
import time
from flask_uploads import UploadSet, configure_uploads, IMAGES
import oracledb
from weasyprint import HTML
import os
from flask_socketio import SocketIO, emit,join_room,leave_room

app = Flask(__name__)
socketio = SocketIO(app)
app.secret_key = "hello"
app.permanent_session_lifetime = timedelta(minutes=10)
user_sids = {}

#oracledb
def get_db_connection():
    # Establishes a connection to the Oracle database.
    connection = oracledb.connect(
       user="system",
       password="123Cs0076",
       dsn="localhost:1521/XEPDB1"
    )
    return connection


photos = UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = 'static/images'
configure_uploads(app,photos)

# @app.route("/")
# def home():
#     return render_template("about.html")


@app.route('/about')
def about():
    return render_template("about.html")


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
       if 'logged_in' in session:
          return f(*args, **kwargs)
       else:
          flash('Unautharized, Please Login', 'danger')
          return redirect(url_for('login'))
    return wrap

def is_admin_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
       if 'admin_logged_in' in session:
          return f(*args, **kwargs)
       elif 'logged_in' in session:
          flash('Unautharized, You are not an admin', 'danger')
          return redirect(url_for('dashboard'))
       else:
          flash('Unautharized, Please Login', 'danger')
          return redirect(url_for('login'))
    return wrap



class emp_form(FlaskForm):
    name = StringField('Name', [validators.DataRequired(), validators.Length(min=1, max=50)],
                       render_kw={"required": ""})
    gender = SelectField('Gender', choices=[('', ''), ('male', 'male'), ('female', 'female'), ('other', 'other')],
                         render_kw={"required": ""})
    email = StringField('Email', [validators.DataRequired(), validators.Length(min=1, max=50), validators.Email()],
                        render_kw={"required": ""})
    # cur = mysql.connection.cursor()
    # result = cur.execute("SELECT department FROM salary");
    department = SelectField('Department', choices=[('', '')], render_kw={"required": ""})
    designation = SelectField('Designation', choices=[('', '')], render_kw={"required": ""})
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.Length(min=5, max=50),
        validators.EqualTo('confirm', message="Password do not match")
    ], render_kw={"required": ""})
    confirm = PasswordField('Confirm Password', render_kw={"required": ""})
    address = StringField('Address', [validators.DataRequired(), validators.Length(min=1, max=500)],
                          render_kw={"required": ""})
    city = StringField('City', [validators.DataRequired(), validators.Length(min=1, max=50)],
                       render_kw={"required": ""})
    state = StringField('State', [validators.DataRequired(), validators.Length(min=1, max=50)],
                        render_kw={"required": ""})
    nationality = StringField('Nationality', [validators.DataRequired(), validators.Length(min=1, max=50)],
                              render_kw={"required": ""})

    pincode = StringField('Pin Code', [validators.DataRequired(), validators.Length(min=1, max=10)],
                          render_kw={"required": ""})
    contact = StringField('Contact', [validators.DataRequired(), validators.Length(min=1, max=10)],
                          render_kw={"required": ""})

class edit_form(FlaskForm):
    name = StringField('Name', [validators.DataRequired(), validators.Length(min = 1,max = 50)],render_kw={"required": ""})
    gender=SelectField('Gender', choices=[('male','male'), ('female','female'), ('other', 'other')],render_kw={"required": ""})
    email = StringField('Email', [validators.DataRequired(),validators.Length(min = 1,max = 50)],render_kw={"required": ""})
    address = StringField('Address', [validators.DataRequired(),validators.Length(min = 1,max = 500)],render_kw={"required": ""})
    city = StringField('City', [validators.DataRequired(),validators.Length(min = 1,max = 50)],render_kw={"required": ""})
    state = StringField('State', [validators.DataRequired(),validators.Length(min = 1,max = 50)],render_kw={"required": ""})
    nationality = StringField('Nationality', [validators.DataRequired(),validators.Length(min = 1,max = 50)],render_kw={"required": ""})
    pincode = StringField('Pin Code', [validators.DataRequired(),validators.Length(min = 1,max = 10)],render_kw={"required": ""})
    contact = StringField('Contact', [validators.DataRequired(),validators.Length(min = 1,max = 10)],render_kw={"required": ""})

class change_dep(FlaskForm):
    emp_id = StringField('Employee ID', [validators.DataRequired()], render_kw={"required": ""} )
    department = SelectField('Department', choices=[('','')],render_kw={"required": ""})
    designation = SelectField('Designation', choices=[('','')],render_kw={"required": ""})

class check_password(FlaskForm):
    old_password = PasswordField('Old Password', [validators.DataRequired(), validators.Length(min = 5,max = 50)],render_kw={"required": ""})
    new_password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.Length(min = 5,max = 50),
        validators.EqualTo('confirm_newpassword', message="Password do not match")
    ],render_kw={"required": ""})
    confirm_newpassword = PasswordField('Confirm Password',render_kw={"required": ""})

class add_dep(FlaskForm):
    department = StringField('Department', [validators.DataRequired(), validators.Length(min = 1,max = 50)],render_kw={"required": ""})
    designation = StringField('Designation', [validators.DataRequired(), validators.Length(min = 1,max = 50)],render_kw={"required": ""})
    salary = StringField('Salary', [validators.DataRequired(), validators.Length(min = 1,max = 50)],render_kw={"required": ""})


class add_des(FlaskForm):
    department = SelectField('Department', choices=[('','')],render_kw={"required": ""})
    designation = StringField('Designation', [validators.DataRequired(), validators.Length(min = 1,max = 50)],render_kw={"required": ""})
    salary = StringField('Salary', [validators.DataRequired(), validators.Length(min = 1,max = 50)],render_kw={"required": ""})

class upd_sal(FlaskForm):
    department = SelectField('Department', choices=[('','')],render_kw={"required": ""})
    designation = SelectField('Designation', choices=[('','')],render_kw={"required": ""})
    salary = StringField('Salary', [validators.DataRequired(), validators.Length(min = 1,max = 50)],render_kw={"required": ""})


@app.route('/')
def index():
    if session.get('logged_in'):
       return redirect(url_for('dashboard'))
    else:
       return redirect(url_for('login'))


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        emp_id = int(request.form['emp_id'])
        password_candidate = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()

        # FIX: Changed the bind variable from `:id` to `:emp_id` to match the column name.
        query = "SELECT emp_id, name, password, admin FROM employee WHERE emp_id = :emp_id"
        # FIX: Changed the dictionary key from 'id' to 'emp_id' to match the bind variable.
        cur.execute(query, {'emp_id': emp_id})
        data = cur.fetchone()

        if data:
            db_emp_id, db_name, db_password, db_admin = data

            if sha256_crypt.verify(password_candidate, db_password):
                session['logged_in'] = True
                session['emp_id'] = db_emp_id
                session['name'] = db_name
                if db_admin >= 1:
                    session['admin_logged_in'] = True
                    flash('You are now logged in as an Admin', 'success')
                else:
                    flash('You are now logged in as an employee', 'success')

                cur.close()
                conn.close()
                return redirect(url_for('dashboard'))
            else:
                error = "Password does not match."
        else:
            error = "Employee ID not found."

        cur.close()
        conn.close()
        return render_template('login.html', error=error)

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("You are now logged out!")
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET','POST'])
@is_logged_in
def dashboard():
    if request.method == 'POST':
       emp_id = session['emp_id']
       conn = get_db_connection()
       curr = conn.cursor()

       if request.form['btn'] == 'attendance':
          from_date = request.form['from']
          to_date = request.form['to']
          if to_date < from_date:
             error = 'To Date cannot be smaller than from Data'
             return render_template('dashboard.html',error=error)

          # FIX: Aligned column names with the provided .sql file (emp_id, att_date)
          query = """
             SELECT COUNT(*) from attendance
             WHERE emp_id = :1 AND att_date BETWEEN TO_DATE(:2, 'YYYY-MM-DD') AND TO_DATE(:3, 'YYYY-MM-DD')
          """
          curr.execute(query, (emp_id,from_date,to_date))
          att_ct = curr.fetchone()[0]

          msg = f'Your attendance from {from_date} to {to_date} is {att_ct}'
          flash(msg,'info')

       elif request.form['btn'] == 'incentive':
          from_date = request.form['fromm']
          to_date = request.form['too']

          if to_date < from_date:
             error = "To date cannot be smaller than from date"
             return render_template('dashboard.html',error=error)

          # FIX: Aligned column names with the provided .sql file (emp_id, inc_date)
          query = """
             SELECT hours FROM incentive
             WHERE emp_id = :1 AND inc_date BETWEEN TO_DATE(:2, 'YYYY-MM-DD') AND TO_DATE(:3, 'YYYY-MM-DD')
          """
          curr.execute(query,(emp_id,from_date,to_date))
          incentive_total_result = curr.fetchall()
          incentive_total = sum([row[0] for row in incentive_total_result if row[0] is not None])

          msg = f"Your incentive from {from_date} to {to_date} is {incentive_total} hours"
          return render_template('dashboard.html',msg=msg)

       curr.close()
       conn.close()
       return render_template('dashboard.html')
    return render_template('dashboard.html')



@app.route('/profile/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def profile(id):
    conn = get_db_connection()
    cur = conn.cursor()
    employee = None

    def fetch_one_as_dict(cursor):
        columns = [desc[0].lower() for desc in cursor.description]
        row = cursor.fetchone()
        return dict(zip(columns, row)) if row else None

    cur.execute("SELECT * FROM e_v WHERE emp_id = :1", [id])
    employee = fetch_one_as_dict(cur)
    cur.close()
    conn.close()

    if employee:
        # --- THIS IS THE NEW PART ---
        # Create a unique number to bust the cache
        cache_buster = int(time.time())
        return render_template('profile.html', employee=employee, cache_buster=cache_buster)
    else:
        flash('Employee Not Found', 'danger')
        return redirect(url_for('dashboard'))


# --- Add this new import at the top of your app.py file ---



# ... (your other imports) ...

# Make sure 'os' and 'time' are imported at the top of your app.py
import os
import time


@app.route('/edit_profile/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_profile(id):
    form = edit_form()

    # Helper to fetch a single row as a dictionary
    def fetch_one_as_dict(cursor):
        columns = [desc[0].lower() for desc in cursor.description]
        row = cursor.fetchone()
        return dict(zip(columns, row)) if row else None

    # This block handles the form submission (POST request)
    if form.validate_on_submit():
        conn = None
        cur = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()

            # Get all the text data from the form
            name = form.name.data
            gender = form.gender.data
            dob = request.form['dob']
            email = form.email.data
            address = form.address.data
            city = form.city.data
            state = form.state.data
            nationality = form.nationality.data
            pincode = form.pincode.data
            contact = form.contact.data

            # Update the main employee table
            cur.execute("""
                UPDATE employee SET name=:1, email=:2, contact=:3, address=:4, dob=TO_DATE(:5,'YYYY-MM-DD'), pincode=:6, gender=:7 WHERE emp_id=:8
            """, (name, email, contact, address, dob, pincode, gender, id))

            # --- THIS IS THE CORRECTED AND COMPLETE CITY/STATE LOGIC ---
            cur.execute("SELECT pincode FROM city_state WHERE pincode=:1", [pincode])
            if not cur.fetchone():
                # If the pincode is new, insert a new record
                cur.execute("INSERT INTO city_state(city, state, pincode) VALUES(:1, :2, :3)", (city, state, pincode))
            else:
                # If the pincode already exists, update its city and state
                cur.execute("UPDATE city_state SET city = :1, state = :2 WHERE pincode = :3", (city, state, pincode))

            # Logic for state_nationality table
            cur.execute("SELECT state FROM state_nationality WHERE state=:1", [state])
            if not cur.fetchone():
                cur.execute("INSERT INTO state_nationality(state, nationality) VALUES(:1, :2)", (state, nationality))

            # File handling logic
            if 'profile_image' in request.files and request.files['profile_image'].filename != '':
                file = request.files['profile_image']
                filename = f"{id}.jpg"
                old_file_path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
                file.filename = filename
                photos.save(file)

            conn.commit()
            flash('Employee details updated successfully!', 'success')
            return redirect(url_for('profile', id=id))

        except Exception as e:
            if conn: conn.rollback()
            flash(f"An error occurred while updating: {e}", "danger")
            print(f"Update Error: {e}")
        finally:
            if cur: cur.close()
            if conn: conn.close()

    # This block handles the initial page load (GET request)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM e_v WHERE emp_id = :1", [id])
    employee = fetch_one_as_dict(cur)
    cur.close()
    conn.close()

    if employee:
        # Pre-fill the form with existing data
        form.name.data = employee.get('name')
        form.gender.data = employee.get('gender')
        form.email.data = employee.get('email')
        form.address.data = employee.get('address')
        form.city.data = employee.get('city')
        form.state.data = employee.get('state')
        form.nationality.data = employee.get('nationality')
        form.pincode.data = str(employee.get('pincode', ''))
        form.contact.data = str(employee.get('contact', ''))
        employee['dob_formatted'] = employee.get('dob').strftime('%Y-%m-%d') if employee.get('dob') else ''
        return render_template('edit_profile.html', form=form, employee=employee)
    else:
        flash('Employee not found.', 'danger')
        return redirect(url_for('dashboard'))


@app.route('/change_password', methods=['GET', 'POST'])
@is_logged_in
def change_password():
    # <<< FIX #1: Use the conventional lowercase variable name `form` >>>
    form = check_password()

    # Use the cleaner, more secure validate_on_submit() method
    if form.validate_on_submit():
        emp_id = session['emp_id']
        old_password = form.old_password.data
        new_password = sha256_crypt.encrypt(str(form.new_password.data))

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT password FROM employee WHERE emp_id = :1", [emp_id])
        data = cur.fetchone()

        if data:
            password = data[0]
            if sha256_crypt.verify(old_password, password):
                cur.execute("UPDATE employee SET password = :1 WHERE emp_id = :2", (new_password, emp_id))
                conn.commit()
                cur.close()
                conn.close()
                flash("Password Changed Successfully!", 'success')
                return redirect(url_for('profile', id=str(emp_id)))
            else:
                flash('Old password does not match.', 'danger')
        else:
            flash('Error: Employee not found.', 'danger')

        cur.close()
        conn.close()
        # Redirect even on failure to prevent form resubmission issues
        return redirect(url_for('change_password'))

    # <<< FIX #2: Pass the correct `form` variable to the template >>>
    return render_template('change_password.html', form=form)




@app.route('/employee/view', methods=['GET', 'POST'])
@is_admin_logged_in
def view_employee():
    conn = get_db_connection()
    employees = []

    # --- Correctly fetch UNIQUE departments and designations ---
    cur_simple = conn.cursor()
    cur_simple.execute("SELECT DISTINCT department FROM salary WHERE department IS NOT NULL")
    depts = sorted([r[0] for r in cur_simple.fetchall()])

    cur_simple.execute("SELECT DISTINCT designation FROM salary WHERE designation IS NOT NULL")
    desigs = sorted([r[0] for r in cur_simple.fetchall()])
    cur_simple.close()

    # Create a new cursor for the main query
    cur = conn.cursor()

    # <<< THE FIX IS HERE: We are re-introducing your successful helper function >>>
    # This function converts the list of tuples from the DB into a list of dictionaries.
    def fetch_as_dict(cursor):
        columns = [desc[0].lower() for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    if request.method == 'POST':
        filters = []
        params = {}

        def add_filter(column, value):
            param_name = f"p_{len(params) + 1}"
            filters.append(f"LOWER({column}) = LOWER(:{param_name})")
            params[param_name] = value

        if request.form.get('cdepartment') and request.form.get('department'):
            add_filter('department', request.form['department'])
        if request.form.get('cdesignation') and request.form.get('designation'):
            add_filter('designation', request.form['designation'])
        if request.form.get('cgender') and request.form.get('gender'):
            add_filter('gender', request.form['gender'])
        if request.form.get('ccity') and request.form.get('city'):
            add_filter('city', request.form['city'])

        if request.form.get('cage'):
            age = int(request.form['age'])
            filters.append("dob <= ADD_MONTHS(SYSDATE, -12 * :age_param)")
            params['age_param'] = age

        query = "SELECT * FROM e_v"
        if filters:
            query += " WHERE " + " AND ".join(filters)

        cur.execute(query, params)
        # <<< THE FIX IS APPLIED HERE >>>
        employees = fetch_as_dict(cur)

        if not employees:
            flash('No employees found matching your filters.', 'warning')
            return render_template('view_employee.html', employees=[], depts=depts, desigs=desigs)

    else:  # This is the GET request
        cur.execute("SELECT * FROM e_v ORDER BY emp_id")
        # <<< AND THE FIX IS APPLIED HERE TOO >>>
        employees = fetch_as_dict(cur)

    cur.close()
    conn.close()

    return render_template('view_employee.html', employees=employees, depts=depts, desigs=desigs)




@app.route('/employee/add', methods=['GET', 'POST'])
@is_admin_logged_in
def add_employee():
    # <<< FIX #1: Use the correct class name `emp_form` and the conventional variable name `form` >>>
    form = emp_form()

    # This logic populates the dropdowns and needs to run every time
    conn_for_choices = get_db_connection()
    if conn_for_choices:
        cur_simple = conn_for_choices.cursor()
        cur_simple.execute("SELECT DISTINCT department, designation FROM salary")
        rows = cur_simple.fetchall()
        depts = sorted(list(set(r[0] for r in rows if r[0])))
        desigs = sorted(list(set(r[1] for r in rows if r[1])))
        # <<< FIX #1: Use the correct variable name `form` >>>
        form.department.choices = [('', 'Select Department')] + [(d, d) for d in depts]
        form.designation.choices = [('', 'Select Designation')] + [(d, d) for d in desigs]
        cur_simple.close()
        conn_for_choices.close()

    # <<< FIX #1: Use the correct variable name `form` >>>
    if form.validate_on_submit():
        conn = None
        cur = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()

            # <<< FIX #1: Get data from the correct `form` object >>>
            name = form.name.data
            gender = form.gender.data
            # <<< FIX #2: Get non-WTForms data from `request.form` >>>
            dob = request.form['dob']
            email = form.email.data
            department = form.department.data
            designation = form.designation.data
            address = form.address.data
            city = form.city.data
            state = form.state.data
            nationality = form.nationality.data
            pincode = form.pincode.data
            contact = form.contact.data
            password = sha256_crypt.encrypt(str(form.password.data))

            cur.execute("SELECT designation FROM salary WHERE department=:1", [department])
            valid_desigs = [r[0] for r in cur.fetchall()]
            if designation not in valid_desigs:
                flash('The chosen combination of department and designation is not available.', 'danger')
                # <<< FIX #1: Pass the correct `form` object to the template >>>
                return render_template('add_employee.html', form=form)

            emp_id_var = cur.var(int)
            sql_insert = """
                INSERT INTO employee (name, email, department, designation, address, contact, password, reg_date, admin, pincode, gender, dob)
                VALUES (:name, :email, :dept, :desig, :addr, :contact, :pwd, SYSDATE, 0, :pincode, :gender, TO_DATE(:dob, 'YYYY-MM-DD'))
                RETURNING emp_id INTO :out_emp_id
            """
            cur.execute(sql_insert, {
                'name': name, 'email': email, 'dept': department, 'desig': designation,
                'addr': address, 'contact': contact, 'pwd': password, 'pincode': pincode,
                'gender': gender, 'dob': dob, 'out_emp_id': emp_id_var
            })
            new_emp_id = emp_id_var.getvalue()[0]

            cur.execute("SELECT pincode FROM city_state WHERE pincode=:1", [pincode])
            if not cur.fetchone():
                cur.execute("INSERT INTO city_state(city, state, pincode) VALUES(:1, :2, :3)", [city, state, pincode])

            cur.execute("SELECT state FROM state_nationality WHERE state=:1", [state])
            if not cur.fetchone():
                cur.execute("INSERT INTO state_nationality(state, nationality) VALUES(:1, :2)", [state, nationality])

            conn.commit()

            if 'profile_image' in request.files and request.files['profile_image'].filename != '':
                file = request.files['profile_image']
                file.filename = f"{new_emp_id}.jpg"
                photos.save(file)

            flash(f'Employee has been successfully added with Employee ID: {new_emp_id}.', 'success')
            return redirect(url_for('add_employee'))

        except oracledb.Error as err:
            if conn:
                conn.rollback()
            error_msg = f"Database Error: {err}"
            print(error_msg)
            flash(f"An error occurred while adding the employee. Error: {err}", 'danger')

        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    # <<< FIX #3: Pass the correct `form` object to the template >>>
    return render_template('add_employee.html', form=form)



@app.route('/attendance', methods=['GET', 'POST'])
@is_admin_logged_in
def attendance():
    if request.method == 'POST':
        emp_id = request.form['emp_id']
        conn = get_db_connection()
        cur = conn.cursor()

        result = cur.execute("SELECT emp_id FROM employee WHERE emp_id = :1", [emp_id])
        if result.fetchone():
            today_str = datetime.datetime.now().strftime('%Y-%m-%d')
            result2 = cur.execute(
                "SELECT emp_id FROM attendance WHERE att_date = TO_DATE(:1, 'YYYY-MM-DD') AND emp_id = :2",
                (today_str, emp_id))
            if result2.fetchone():
                error = 'Today\'s attendance is already marked for this employee'
                cur.close()
                conn.close()
                return render_template('attendance.html', error=error)
            else:
                cur.execute("INSERT INTO attendance(att_date, emp_id) VALUES(TO_DATE(:1, 'YYYY-MM-DD'), :2)",
                            (today_str, emp_id))
                conn.commit()
                msg = 'Attendance marked succesfully for employee with Employee ID ' + str(emp_id)
                cur.close()
                conn.close()
                return render_template('attendance.html', msg=msg)
        else:
            error = 'Employee id not found'
            cur.close()
            conn.close()
            return render_template('attendance.html', error=error)
    return render_template('attendance.html')


@app.route('/incentive', methods=['GET', 'POST'])
@is_admin_logged_in
def incentive():
    if request.method == 'POST':
        emp_id = request.form['emp_id']
        hours = request.form['hours']
        conn = get_db_connection()
        cur = conn.cursor()

        result = cur.execute("SELECT emp_id FROM employee WHERE emp_id = :1", [emp_id])
        if result.fetchone():
            today_str = datetime.datetime.now().strftime('%Y-%m-%d')
            result2 = cur.execute(
                "SELECT emp_id FROM incentive WHERE inc_date = TO_DATE(:1, 'YYYY-MM-DD') AND emp_id = :2",
                (today_str, emp_id))
            if result2.fetchone():
                error = 'Today\'s incentive is already added for this employee'
                cur.close()
                conn.close()
                return render_template('incentive.html', error=error)
            else:
                cur.execute("INSERT INTO incentive(inc_date, hours, emp_id) VALUES(TO_DATE(:1, 'YYYY-MM-DD'), :2, :3)",
                            (today_str, hours, emp_id))
                conn.commit()
                msg = 'Incentive added succesfully for employee with Employee id ' + str(emp_id)
                cur.close()
                conn.close()
                return render_template('incentive.html', msg=msg)
        else:
            error = 'Employee id not found'
            cur.close()
            conn.close()
            return render_template('incentive.html', error=error)
    return render_template('incentive.html')


from datetime import date, timedelta
import datetime  # Make sure this is imported at the top of your file
import pdfkit  # Make sure this is imported at the top of your file

# --- Add this new import at the top of your app.py file ---


# You can now remove 'import pdfkit' and 'import make_response' if they are not used elsewhere

# --- Make sure these imports are at the top of your app.py file ---




@app.route('/salary', methods=['GET', 'POST'])
@is_admin_logged_in
def salary():
    if request.method == 'POST':
        emp_id = request.form['emp_id']
        from_date_str = request.form['from']
        to_date_str = request.form['to']

        if to_date_str < from_date_str:
            flash('"To Date" cannot be earlier than "From Date".', 'danger')
            return redirect(url_for('salary'))

        conn = None
        cur = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()

            def fetch_one_as_dict(cursor):
                columns = [desc[0].lower() for desc in cursor.description]
                row = cursor.fetchone()
                return dict(zip(columns, row)) if row else None

            # <<< --- THIS IS THE CRITICAL MISSING BLOCK THAT IS NOW RESTORED --- >>>
            cur.execute("SELECT * FROM e_v WHERE emp_id = :1", [emp_id])
            emp_data = fetch_one_as_dict(cur)
            # <<< --- END OF MISSING BLOCK --- >>>

            if emp_data:
                cur.execute("SELECT amount_per_hour FROM salary WHERE department = :1 AND designation = :2",
                            (emp_data['department'], emp_data['designation']))
                salary_data = cur.fetchone()

                if not salary_data:
                    flash("Salary structure not found for this employee's role.", "danger")
                    return redirect(url_for('salary'))

                att_ct = 0
                if emp_data.get('designation', '').lower() == 'ceo':
                    working_days = 0
                    from_date = datetime.datetime.strptime(from_date_str, '%Y-%m-%d').date()
                    to_date = datetime.datetime.strptime(to_date_str, '%Y-%m-%d').date()
                    delta = to_date - from_date
                    for i in range(delta.days + 1):
                        day = from_date + timedelta(days=i)
                        if day.weekday() < 5:
                            working_days += 1
                    att_ct = working_days
                else:
                    cur.execute(
                        "SELECT COUNT(*) FROM attendance WHERE emp_id = :1 AND att_date BETWEEN TO_DATE(:2, 'YYYY-MM-DD') AND TO_DATE(:3, 'YYYY-MM-DD')",
                        (emp_id, from_date_str, to_date_str))
                    att_ct = cur.fetchone()[0]

                cur.execute(
                    "SELECT SUM(hours) FROM incentive WHERE emp_id = :1 AND inc_date BETWEEN TO_DATE(:2, 'YYYY-MM-DD') AND TO_DATE(:3, 'YYYY-MM-DD')",
                    (emp_id, from_date_str, to_date_str))
                incent_res = cur.fetchone()
                incent_tot = incent_res[0] if incent_res and incent_res[0] is not None else 0

                salary_tot = salary_data[0] * ((att_ct * 10) + incent_tot)

                if request.form['btn'] == 'cal':
                    msg = f"Salary for employee {emp_data['name']} ({emp_id}) from {from_date_str} to {to_date_str} is {salary_tot:,.2f}"
                    flash(msg, 'success')

                elif request.form['btn'] == 'gen':
                    try:
                        rendered = render_template('payroll.html', employee=emp_data, fro=from_date_str, to=to_date_str,
                                                   salary=f"{salary_tot:,.2f}")
                        pdf = HTML(string=rendered).write_pdf()
                        response = make_response(pdf)
                        response.headers['Content-Type'] = 'application/pdf'
                        response.headers['Content-Disposition'] = 'inline; filename=payroll.pdf'
                        return response
                    except Exception as e:
                        print(f"PDF Generation Error: {e}")
                        flash(f"Error: Could not generate PDF. {e}", "danger")
            else:
                flash('Employee ID not found', 'danger')

        except oracledb.Error as err:
            flash(f"A database error occurred: {err}", "danger")
            print(f"Database Error: {err}")  # For your debugging
        finally:
            if cur: cur.close()
            if conn: conn.close()

        return redirect(url_for('salary'))

    return render_template('salary.html')



@app.route('/employee/change_department', methods=['GET', 'POST'])
@is_admin_logged_in
def change_department():
    # <<< FIX #1: Instantiate the form correctly (no request.form needed) >>>
    # <<< FIX #2: Use the conventional lowercase variable name `form` >>>
    form = change_dep()
    conn = get_db_connection()
    cur_ = conn.cursor()

    # --- This logic populates the dropdowns and needs to run for GET and POST ---
    cur_.execute("SELECT DISTINCT department, designation FROM salary")
    rows = cur_.fetchall()
    depts = sorted(list(set(r[0] for r in rows if r[0])))
    desigs = sorted(list(set(r[1] for r in rows if r[1])))
    # <<< FIX #2: Use the correct variable name `form` >>>
    form.department.choices = [('', 'Select Department')] + [(d, d) for d in depts]
    form.designation.choices = [('', 'Select Designation')] + [(d, d) for d in desigs]
    cur_.close()

    # <<< FIX #3: Use the validate_on_submit() method >>>
    if form.validate_on_submit():
        emp_id = form.emp_id.data
        department = form.department.data
        designation = form.designation.data

        cur = conn.cursor()
        cur.execute("SELECT emp_id FROM employee WHERE emp_id = :1", [emp_id])
        if cur.fetchone():
            # Check if the new combination is valid
            cur.execute("SELECT designation FROM salary WHERE department=:1", [department])
            valid_desigs = [r[0] for r in cur.fetchall()]
            if designation in valid_desigs:
                cur.execute("UPDATE employee SET designation = :1, department = :2 WHERE emp_id = :3",
                            (designation, department, emp_id))
                conn.commit()
                flash(f"Employee {emp_id}'s department and designation updated successfully.", 'success')
            else:
                flash('Invalid Department/Designation combination.', 'danger')
        else:
            flash('Employee ID not found.', 'danger')

        cur.close()
        conn.close()
        # Redirect after processing the POST request
        return redirect(url_for('change_department'))

    # This handles the GET request (initial page load)
    conn.close()
    # <<< FIX #4: Pass the correct `form` variable to the template >>>
    return render_template('change_department.html', form=form)


@app.route('/hierarchy', methods=['GET', 'POST'])
@is_admin_logged_in
def hierarchy():
    # Instantiate all FlaskForms without request.form
    form1 = add_dep()
    form2 = add_des()
    form3 = upd_sal()

    conn = get_db_connection()
    cur = conn.cursor()

    # --- This logic populates the dropdowns ---
    cur.execute("SELECT DISTINCT department, designation FROM salary")
    rows = cur.fetchall()
    depts = sorted(list(set(r[0] for r in rows if r[0])))
    desigs = sorted(list(set(r[1] for r in rows if r[1])))
    form2.department.choices = [('', 'Select Department')] + [(i, i) for i in depts]
    form3.department.choices = [('', 'Select Department')] + [(i, i) for i in depts]
    form3.designation.choices = [('', 'Select Designation')] + [(i, i) for i in desigs]

    # --- This logic handles the POST request ---
    if request.method == 'POST':
        btn_action = request.form.get('btn')
        action_successful = False # Flag to track if any action was successful

        # Validate each form individually based on which button was pressed
        if btn_action == 'form1' and form1.validate():
            try:
                cur.execute("INSERT INTO salary(department,designation,amount_per_hour) VALUES(:1, :2, :3)",
                            (form1.department.data, form1.designation.data, int(form1.salary.data)))
                conn.commit()
                flash('New Department and Designation added.', 'success')
                action_successful = True
            except oracledb.Error as e:
                conn.rollback()
                flash(f"Error adding Department/Designation: {e}", "danger")

        elif btn_action == 'form2' and form2.validate():
            try:
                cur.execute("INSERT INTO salary(department,designation,amount_per_hour) VALUES(:1, :2, :3)",
                            (form2.department.data, form2.designation.data, int(form2.salary.data)))
                conn.commit()
                flash('New Designation added to existing Department.', 'success')
                action_successful = True
            except oracledb.Error as e:
                conn.rollback()
                flash(f"Error adding Designation: {e}", "danger")

        elif btn_action == 'form3' and form3.validate():
            try:
                cur.execute("UPDATE salary SET amount_per_hour=:1 WHERE department=:2 AND designation=:3",
                            (int(form3.salary.data), form3.department.data, form3.designation.data))
                conn.commit()
                flash('Salary updated successfully.', 'success')
                action_successful = True
            except oracledb.Error as e:
                conn.rollback()
                flash(f"Error updating Salary: {e}", "danger")
        else:
             # Handle validation errors if a button was pressed but form invalid
             if btn_action in ['form1', 'form2', 'form3']:
                 flash('Please correct the errors in the form and try again.', 'danger')

        cur.close()
        conn.close()
        # Redirect only if an action was attempted (to prevent losing error messages)
        if btn_action:
             return redirect(url_for('hierarchy'))

    # --- This handles the GET request (initial page load) ---
    cur.close()
    conn.close()
    return render_template('hierarchy.html', form1=form1, form2=form2, form3=form3)

@app.route('/make_admin/<string:id>', methods=['POST'])
@is_admin_logged_in
def make_admin(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE employee SET admin=1 WHERE emp_id=:1", [id])
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "done"}), 200


@app.route('/remove_admin/<string:id>', methods=['POST'])
@is_admin_logged_in
def remove_admin(id):
    if int(id) == 1:
        return jsonify({"error": "Cannot remove from admin"}), 400
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE employee SET admin=0 WHERE emp_id=:1", [id])
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "done"}), 200


@app.route('/delete/<string:id>', methods=['POST'])
@is_admin_logged_in
def del_emp(id):
    if int(id) == 1:
        return jsonify({"error": "cannot remove"}), 400
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM employee WHERE emp_id = :1", [id])
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "done"}), 200

# Add this new route anywhere in your app.py
@app.route('/get_designations/<string:department_name>')
@is_admin_logged_in # Protect the endpoint
def get_designations(department_name):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT designation FROM salary WHERE department = :1 AND designation IS NOT NULL ORDER BY designation", [department_name])
    # Fetch all rows and extract the first element (designation) from each tuple
    designations = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(designations) # Return the list as JSON

@app.context_processor
def inject_current_year():
    return {'current_year': datetime.date.today().year}


# --- Helper Function (Ensure fetch_all_as_dict is defined) ---
def fetch_all_as_dict(cursor):
    if not cursor.description: return []
    columns = [desc[0].lower() for desc in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


# --- Chat Route (Loads relevant history and employee list) ---
@app.route('/chat')
@is_logged_in
def chat():
    emp_id = session['emp_id']
    conn, cur = None, None
    chat_history = []
    employee_list = []
    try:
        conn = get_db_connection()
        if not conn: raise oracledb.Error("DB connection failed")
        cur = conn.cursor()

        # Fetch messages WHERE the current user is sender OR recipient
        cur.rowfactory = lambda *args: dict(zip([d[0].lower() for d in cur.description], args))  # Set rowfactory
        cur.execute("""
            SELECT
                cm.message_id, cm.sender_id, sender.name as sender_name,
                cm.recipient_id, recipient.name as recipient_name,
                cm.message_text, cm.sent_at, cm.message_type
            FROM chat_messages cm
            JOIN employee sender ON cm.sender_id = sender.emp_id
            LEFT JOIN employee recipient ON cm.recipient_id = recipient.emp_id
            WHERE cm.sender_id = :current_user OR cm.recipient_id = :current_user
            ORDER BY cm.sent_at ASC
        """, {'current_user': emp_id})
        chat_history = cur.fetchall()  # Returns list of dicts

        # Fetch list of all employees (including self) for the recipient dropdown
        cur.rowfactory = None  # Reset rowfactory
        cur.execute("SELECT emp_id, name FROM employee ORDER BY name ASC")
        employee_list = fetch_all_as_dict(cur)  # Use helper

    except oracledb.Error as err:
        flash(f"Error fetching chat data: {err}", "danger")
        print(f"Chat Load Error: {err}")
    finally:
        if cur: cur.close()
        if conn: conn.close()

    return render_template('chat.html',
                           chat_history=chat_history,
                           employee_list=employee_list)


@socketio.on('connect')
def handle_connect(auth=None):
    """Track connected users and join their personal chat room."""
    if 'emp_id' not in session:
        return False

    emp_id = session['emp_id']
    name = session.get('name', f'User {emp_id}')
    user_sids[emp_id] = {'sid': request.sid, 'name': name}

    join_room(str(emp_id))  # ✅ Each user joins their unique room
    print(f"--- SocketIO: {name} (ID: {emp_id}) joined room {emp_id} ---")

    # Send past messages
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT cm.sender_id, s.name AS sender_name,
                   cm.recipient_id, r.name AS recipient_name,
                   cm.message_text, cm.sent_at
            FROM chat_messages cm
            JOIN employee s ON cm.sender_id = s.emp_id
            LEFT JOIN employee r ON cm.recipient_id = r.emp_id
            WHERE cm.sender_id = :emp OR cm.recipient_id = :emp
            ORDER BY cm.sent_at ASC
        """, {'emp': emp_id})
        past_msgs = fetch_all_as_dict(cur)

        # Convert datetime to ISO strings
        for msg in past_msgs:
            if isinstance(msg.get('sent_at'), datetime.datetime):
                msg['sent_at'] = msg['sent_at'].isoformat()

        emit('load_history', past_msgs, room=request.sid)

    except Exception as e:
        print(f"Error loading past messages: {e}")
    finally:
        cur.close()
        conn.close()


@socketio.on('disconnect')
def handle_disconnect(sid):
    """Remove disconnected users from tracking."""
    disconnected_emp_id = None
    for emp_id, u_info in list(user_sids.items()):
        if u_info['sid'] == sid:  # ← use the sid argument directly
            disconnected_emp_id = emp_id
            break

    if disconnected_emp_id:
        user_sids.pop(disconnected_emp_id, None)
        print(f"--- SocketIO: Client disconnected: (ID: {disconnected_emp_id}) ---")


@socketio.on('message')
def handle_message(data):
    """Handles incoming messages, saves to DB, emits to recipient and sender."""
    if 'emp_id' not in session: return
    sender_id = session['emp_id']
    sender_name = session.get('name', f'User {sender_id}')
    target_id_str = data.get('target_id')
    message_text = data.get('msg')

    if not message_text or not message_text.strip(): return
    if not target_id_str:
        emit('message', {'msg': "Please select a recipient.", 'sender_name': 'System', 'type': 'system'},
             room=request.sid)
        return

    try:
        recipient_id = int(target_id_str)
        message_db_type = 'private'  # All messages are P2P
    except (ValueError, TypeError):
        emit('message', {'msg': "Invalid recipient ID selected.", 'sender_name': 'System', 'type': 'system'},
             room=request.sid)
        return

    # Fetch recipient name
    recipient_name = f"User {recipient_id}"  # Fallback
    recipient_info_live = user_sids.get(recipient_id)
    if recipient_info_live:
        recipient_name = recipient_info_live['name']
    else:
        conn_name, cur_name = None, None
        try:
            conn_name = get_db_connection()
            cur_name = conn_name.cursor()
            cur_name.execute("SELECT name FROM employee WHERE emp_id = :1", [recipient_id])
            name_result = cur_name.fetchone()
            if name_result: recipient_name = name_result[0]
        except Exception as e:
            print(f"Error fetching recipient name: {e}")
        finally:
            if cur_name: cur_name.close()
            if conn_name: conn_name.close()

    response_data = {
        'msg': message_text, 'sender_name': sender_name, 'sender_id': sender_id,
        'recipient_id': recipient_id, 'recipient_name': recipient_name,
        'sent_at': datetime.datetime.now().isoformat(), 'type': message_db_type
    }

    # --- Save Message to Database ---
    conn, cur = None, None
    message_saved = False
    try:
        conn = get_db_connection()
        if not conn:
            raise oracledb.Error("DB connection failed")
        cur = conn.cursor()
        print(f"--- DEBUG: Saving msg. Sender:{sender_id}, Recipient:{recipient_id} ---")

        # FIXED INSERT (remove message_type)
        cur.execute("""
            INSERT INTO chat_messages (sender_id, recipient_id, message_text)
            VALUES (:sender, :recipient, :msg)
        """, {
            'sender': sender_id,
            'recipient': recipient_id,
            'msg': message_text
        })

        conn.commit()
        message_saved = True
        print("--- DEBUG: Message saved successfully. ---")

    except oracledb.Error as e:  # fixed typo
        if conn: conn.rollback()
        print(f"!!!!!!!!!! Chat DB SAVE ERROR: {e} !!!!!!!!!!!")
        emit('message', {'msg': f"Error saving message: {e}", 'sender_name': 'System', 'type': 'system'},
             room=request.sid)
    finally:
        if cur: cur.close()
        if conn: conn.close()

    # --- Emit Live Message ONLY if saved successfully ---
    if message_saved:
        response_data = {
            'msg': message_text,
            'sender_name': sender_name,
            'sender_id': sender_id,
            'recipient_id': recipient_id,
            'recipient_name': recipient_name,
            'sent_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'type': message_db_type
        }

        # ✅ Emit to recipient's room
        emit('message', response_data, room=str(recipient_id))

        # ✅ Emit to sender's room (so they also see their message)
        emit('message', response_data, room=str(sender_id))

if __name__ == "__main__":
    socketio.run(app, debug=True)

