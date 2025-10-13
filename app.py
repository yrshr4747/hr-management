from flask import Flask, render_template, flash, redirect, request, url_for, session, logging, jsonify, make_response
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, validators, SelectField,FileField
from flask_wtf.file import FileField
from passlib.hash import sha256_crypt
from functools import wraps
from datetime import timedelta
from werkzeug.utils import secure_filename
# from flask_reuploaded import UploadSet, configure_uploads, IMAGES
# import pdfkit
from flask_uploads import UploadSet, configure_uploads, IMAGES
import oracledb

app = Flask(__name__)
app.secret_key = "hello"
app.permanent_session_lifetime = timedelta(minutes=10)

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
                if db_admin == 1:
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

       if request.FlaskForm['btn'] == 'attendance':
          from_date = request.FlaskForm['from']
          to_date = request.FlaskForm['to']
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

       elif request.FlaskForm['btn'] == 'incentive':
          from_date = request.FlaskForm['fromm']
          to_date = request.FlaskForm['too']

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
    employee = None  # Initialize employee to None

    # Helper to convert Oracle row tuples to dicts with lowercase keys
    # This is your successful pattern from view_employee
    def fetch_as_dict(cursor):
        columns = [desc[0].lower() for desc in cursor.description]
        # fetchone() returns a single tuple or None
        row = cursor.fetchone()
        if row:
            return dict(zip(columns, row))
        return None

    # <<< FIX #2: The SQL query now correctly uses emp_id >>>
    cur.execute("SELECT * FROM e_v WHERE emp_id = :1", [id])

    # <<< FIX #1: Using the new fetch_as_dict pattern >>>
    employee = fetch_as_dict(cur)

    cur.close()
    conn.close()

    if employee:
        # The session.emp_id is an integer, the URL id is a string.
        # We need to compare them correctly.
        if str(session.get('emp_id')) == str(employee.get('emp_id')):
            session['is_own_profile'] = True
        else:
            session['is_own_profile'] = False

        return render_template('profile.html', employee=employee)
    else:
        flash('Employee Not Found', 'danger')
        return redirect(url_for('dashboard'))


@app.route('/edit_profile/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_profile(id):
    FlaskForm = edit_FlaskForm()
    conn = get_db_connection()
    cur = conn.cursor()

    # Helper to fetch a single row as a dictionary
    def fetch_one_as_dict(cursor):
        columns = [desc[0].lower() for desc in cursor.description]
        row = cursor.fetchone()
        return dict(zip(columns, row)) if row else None

    # <<< CHANGE #1: Using validate_on_submit() for the main logic >>>
    if FlaskForm.validate_on_submit():
        try:
            name = FlaskForm.name.data
            gender = FlaskForm.gender.data
            dob = request.FlaskForm['dob']
            email = FlaskForm.email.data
            address = FlaskForm.address.data
            city = FlaskForm.city.data
            state = FlaskForm.state.data
            nationality = FlaskForm.nationality.data
            pincode = FlaskForm.pincode.data
            contact = FlaskForm.contact.data

            cur.execute("""
                UPDATE employee SET name=:1, email=:2, contact=:3, address=:4, dob=TO_DATE(:5,'YYYY-MM-DD'), pincode=:6, gender=:7 WHERE emp_id=:8
            """, (name, email, contact, address, dob, pincode, gender, id))

            cur.execute("SELECT pincode FROM city_state WHERE pincode=:1", [pincode])
            if not cur.fetchone():
                cur.execute("INSERT INTO city_state(city, state, pincode) VALUES(:1, :2, :3)", (city, state, pincode))

            cur.execute("SELECT state FROM state_nationality WHERE state=:1", [state])
            if not cur.fetchone():
                cur.execute("INSERT INTO state_nationality(state, nationality) VALUES(:1, :2)", (state, nationality))

            conn.commit()

            if 'profile_image' in request.files and request.files['profile_image'].filename != '':
                file = request.files['profile_image']
                file.filename = f"{id}.jpg"
                photos.save(file)

            flash('Employee details updated successfully!', 'success')
            return redirect(url_for('profile', id=id))

        except oracledb.Error as err:
            conn.rollback()
            flash(f"Database error: {err}", "danger")
        finally:
            cur.close()
            conn.close()

    # <<< CHANGE #2: Logic for GET request to pre-populate the FlaskForm >>>
    cur.execute("SELECT * FROM e_v WHERE emp_id = :1", [id])
    employee = fetch_one_as_dict(cur)
    cur.close()
    conn.close()

    if employee:
        # This pre-fills the FlaskForm with existing data when the page loads
        FlaskForm.name.data = employee.get('name')
        FlaskForm.gender.data = employee.get('gender')
        FlaskForm.email.data = employee.get('email')
        FlaskForm.address.data = employee.get('address')
        FlaskForm.city.data = employee.get('city')
        FlaskForm.state.data = employee.get('state')
        FlaskForm.nationality.data = employee.get('nationality')
        FlaskForm.pincode.data = str(employee.get('pincode', ''))
        FlaskForm.contact.data = str(employee.get('contact', ''))
        # Pass the FlaskFormatted date separately for the HTML date input
        employee['dob_FlaskFormatted'] = employee.get('dob').strftime('%Y-%m-%d') if employee.get('dob') else ''
        return render_template('edit_profile.html', FlaskForm=FlaskForm, employee=employee)
    else:
        flash('Employee not found.', 'danger')
        return redirect(url_for('dashboard'))


@app.route('/change_password', methods=['GET', 'POST'])
@is_logged_in
def change_password():
    FlaskForm = check_password()

    # <<< CHANGE: Using validate_on_submit() >>>
    if FlaskForm.validate_on_submit():
        emp_id = session['emp_id']
        old_password = FlaskForm.old_password.data
        new_password = sha256_crypt.encrypt(str(FlaskForm.new_password.data))

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
                flash("Password Changed Successfully", 'success')
                return redirect(url_for('profile', id=str(emp_id)))
            else:
                flash('Old password does not match.', 'danger')
        cur.close()
        conn.close()

    return render_template('change_password.html', FlaskForm=FlaskForm)


# @app.route('/employee/view', methods=['GET', 'POST'])
# @is_admin_logged_in
# def view_employee():
#     conn = get_db_connection()
#     cur = conn.cursor()
#
#     cur.execute("SELECT department, designation FROM salary")
#     rows = cur.fetchall()
#     depts = sorted(list(set(r[0] for r in rows if r[0])))
#     desigs = sorted(list(set(r[1] for r in rows if r[1])))
#
#     # Use the rowfactory for dictionary results
#     cur.rowfactory = lambda *args: dict(zip([d[0].lower() for d in cur.description], args))
#
#     if request.method == 'POST':
#         filters = []
#         params = []
#         param_idx = 1
#
#         def add_filter(field, value):
#             nonlocal param_idx
#             filters.append(f"{field} = :{param_idx}")
#             params.append(value)
#             param_idx += 1
#
#         if request.FlaskForm.get('cdepartment'): add_filter('department', request.FlaskForm['department'])
#         if request.FlaskForm.get('cdesignation'): add_filter('designation', request.FlaskForm['designation'])
#         if request.FlaskForm.get('cgender'): add_filter('gender', request.FlaskForm['gender'])
#         if request.FlaskForm.get('ccity'): add_filter('city', request.FlaskForm['city'])
#         if request.FlaskForm.get('cstate'): add_filter('state', request.FlaskForm['state'])
#
#         if request.FlaskForm.get('cage'):
#             age = int(request.FlaskForm['age'])
#             filters.append(f"dob >= ADD_MONTHS(SYSDATE, -12 * :{param_idx})")
#             params.append(age)
#             param_idx += 1
#
#         query = "SELECT * FROM e_v"
#         if filters:
#             query += " WHERE " + " AND ".join(filters)
#
#         cur.execute(query, params)
#         employees = cur.fetchall()
#
#         if not employees:
#             flash('No employees found matching your filters.', 'warning')
#
#     else:  # This is the GET request (first page load)
#         # Fetch ALL employees by default
#         cur.execute("SELECT * FROM e_v ORDER BY emp_id")  # <<< THE FIX IS HERE
#         employees = cur.fetchall()
#
#     cur.close()
#     conn.close()
#
#     return render_template('view_employee.html', employees=employees, depts=depts, desigs=desigs)


@app.route('/employee/view', methods=['GET', 'POST'])
@is_admin_logged_in
def view_employee():
    conn = get_db_connection()

    # Fetch distinct department and designation for filters
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT department, designation FROM salary")
    rows = cur.fetchall()
    depts = sorted([r[0] for r in rows if r[0]])
    desigs = sorted([r[1] for r in rows if r[1]])

    employees = []
    error_msg = None

    # Helper to convert Oracle row tuples to dicts with lowercase keys
    def fetch_as_dict(cursor):
        columns = [desc[0].lower() for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    if request.method == 'POST':
        filters = []
        params = []

        def add_filter(column, value):
            filters.append(f"LOWER({column}) = LOWER(:{len(params) + 1})")
            params.append(value)

        if request.form.get('cdepartment'):
            add_filter('department', request.form['department'])
        if request.form.get('cdesignation'):
            add_filter('designation', request.form['designation'])
        if request.form.get('cgender'):
            add_filter('gender', request.form['gender'])
        if request.form.get('ccity'):
            add_filter('city', request.form['city'])
        if request.form.get('cstate'):
            add_filter('state', request.form['state'])
        if request.form.get('cage'):
            age = int(request.form['age'])
            filters.append(f"dob >= ADD_MONTHS(SYSDATE, -12 * :{len(params) + 1})")
            params.append(age)

        query = "SELECT * FROM e_v"
        if filters:
            query += " WHERE " + " AND ".join(filters)

        cur.execute(query, params)
        employees = fetch_as_dict(cur)

        if not employees:
            error_msg = "No employees found matching your filters."
    else:
        cur.execute("SELECT * FROM e_v ORDER BY emp_id")
        employees = fetch_as_dict(cur)

    cur.close()
    conn.close()

    return render_template(
        'view_employee.html',
        employees=employees,
        depts=depts,
        desigs=desigs,
        error=error_msg
    )


import datetime
import oracledb
from passlib.hash import sha256_crypt


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
        emp_id = request.FlaskForm['emp_id']
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
        emp_id = request.FlaskForm['emp_id']
        hours = request.FlaskForm['hours']
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


@app.route('/salary', methods=['GET', 'POST'])
@is_admin_logged_in
def salary():
    if request.method == 'POST':
        emp_id = request.form['emp_id']
        from_date = request.form['from']
        to_date = request.form['to']

        if to_date < from_date:
            flash('To Date cannot be smaller than From Date', 'danger')
            return render_template('salary.html')

        conn = get_db_connection()
        cur = conn.cursor()

        # <<< CHANGE #1: Define the helper function to convert the row to a dictionary >>>
        def fetch_one_as_dict(cursor):
            columns = [desc[0].lower() for desc in cursor.description]
            row = cursor.fetchone()
            return dict(zip(columns, row)) if row else None

        cur.execute("SELECT * FROM e_v WHERE emp_id = :1", [emp_id])
        # <<< CHANGE #2: Use the helper function to create emp_data as a dictionary >>>
        emp_data = fetch_one_as_dict(cur)

        if emp_data:
            # <<< CHANGE #3: Use lowercase keys to access the dictionary >>>
            cur.execute("SELECT amount_per_hour FROM salary WHERE department = :1 AND designation = :2",
                        (emp_data['department'], emp_data['designation']))
            salary_data = cur.fetchone()

            if not salary_data:
                flash("Salary structure not found for this employee's role.", "danger")
                cur.close()
                conn.close()
                return render_template('salary.html')

            cur.execute(
                "SELECT COUNT(*) FROM attendance WHERE emp_id = :1 AND att_date BETWEEN TO_DATE(:2, 'YYYY-MM-DD') AND TO_DATE(:3, 'YYYY-MM-DD')",
                (emp_id, from_date, to_date))
            att_ct = cur.fetchone()[0]

            cur.execute(
                "SELECT SUM(hours) FROM incentive WHERE emp_id = :1 AND inc_date BETWEEN TO_DATE(:2, 'YYYY-MM-DD') AND TO_DATE(:3, 'YYYY-MM-DD')",
                (emp_id, from_date, to_date))
            incent_res = cur.fetchone()
            incent_tot = incent_res[0] if incent_res and incent_res[0] is not None else 0

            salary_tot = salary_data[0] * ((att_ct * 10) + incent_tot)

            if request.form['btn'] == 'cal':
                msg = f"Salary for employee {emp_data['name']} ({emp_id}) from {from_date} to {to_date} is {salary_tot:,.2f}"
                flash(msg, 'success')
            elif request.form['btn'] == 'gen':
                rendered = render_template('payroll.html', employee=emp_data, fro=from_date, to=to_date,
                                           salary=f"{salary_tot:,.2f}")
                try:
                    pdf = pdfkit.from_string(rendered, False)
                    response = make_response(pdf)
                    response.headers['Content-Type'] = 'application/pdf'
                    response.headers['Content-Disposition'] = 'inline; filename=payroll.pdf'
                    cur.close()
                    conn.close()
                    return response
                except OSError:
                    flash("Error: Could not generate PDF. 'wkhtmltopdf' may not be installed or in your system's PATH.",
                          "danger")
        else:
            flash('Employee ID not found', 'danger')

        cur.close()
        conn.close()

    return render_template('salary.html')


@app.route('/employee/change_department', methods=['GET', 'POST'])
@is_admin_logged_in
def change_department():
    FlaskForm = change_dep(request.FlaskForm)
    conn = get_db_connection()
    cur_ = conn.cursor()

    cur_.execute("SELECT department, designation FROM salary")
    rows = cur_.fetchall()
    depts = sorted(list(set(r[0] for r in rows if r[0])))
    desigs = sorted(list(set(r[1] for r in rows if r[1])))
    FlaskForm.department.choices = [('', '')] + [(d, d) for d in depts]
    FlaskForm.designation.choices = [('', '')] + [(d, d) for d in desigs]
    cur_.close()

    if request.method == 'POST' and FlaskForm.validate():
        emp_id, department, designation = FlaskForm.emp_id.data, FlaskForm.department.data, FlaskForm.designation.data
        cur = conn.cursor()
        result = cur.execute("SELECT emp_id FROM employee WHERE emp_id = :1", [emp_id])
        if result.fetchone():
            cur.execute("UPDATE employee SET designation = :1, department = :2 WHERE emp_id=:3",
                        (designation, department, emp_id))
            conn.commit()
            flash('Employee details updated successfully.', 'success')
        else:
            flash('Employee id not found', 'danger')
        cur.close()
        conn.close()
        return redirect(url_for('change_department'))

    conn.close()
    return render_template('change_department.html', FlaskForm=FlaskForm)


@app.route('/hierarchy', methods=['GET', 'POST'])
@is_admin_logged_in  # Changed from is_logged_in for consistency
def hierarchy():
    # <<< CHANGE: Instantiate all FlaskForms without request.FlaskForm >>>
    form1 = add_dep()
    form2 = add_des()
    form3 = upd_sal()

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT DISTINCT department, designation FROM salary")
    rows = cur.fetchall()
    depts = sorted(list(set(r[0] for r in rows if r[0])))
    desigs = sorted(list(set(r[1] for r in rows if r[1])))
    form2.department.choices = [('', 'Select Department')] + [(i, i) for i in depts]
    form3.department.choices = [('', 'Select Department')] + [(i, i) for i in depts]
    form3.designation.choices = [('', 'Select Designation')] + [(i, i) for i in desigs]

    # <<< CHANGE: We stick with this logic for multiple FlaskForms >>>
    if request.method == 'POST':
        btn_action = request.form.get('btn')

        # <<< CHANGE: Validate each FlaskForm individually >>>
        if btn_action == 'form1' and form1.validate():
            cur.execute("INSERT INTO salary(department,designation,amount_per_hour) VALUES(:1, :2, :3)",
                        (form1.department.data, form1.designation.data, int(form1.salary.data)))
            flash('New Department and Designation added.', 'success')
            conn.commit()
        elif btn_action == 'form2' and form2.validate():
            cur.execute("INSERT INTO salary(department,designation,amount_per_hour) VALUES(:1, :2, :3)",
                        (form2.department.data, form2.designation.data, int(form2.salary.data)))
            flash('New Designation added to existing Department.', 'success')
            conn.commit()
        elif btn_action == 'form3' and form3.validate():
            cur.execute("UPDATE salary SET amount_per_hour=:1 WHERE department=:2 AND designation=:3",
                        (int(form3.salary.data), form3.department.data, form3.designation.data))
            flash('Salary updated successfully.', 'success')
            conn.commit()

        cur.close()
        conn.close()
        return redirect(url_for('hierarchy'))

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








if __name__ == "__main__":
    app.run(debug=True)

