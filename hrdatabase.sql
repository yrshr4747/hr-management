-- Drop tables if they exist
BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE attendance CASCADE CONSTRAINTS';
EXCEPTION
   WHEN OTHERS THEN NULL;
END;
/

BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE city_state CASCADE CONSTRAINTS';
EXCEPTION
   WHEN OTHERS THEN NULL;
END;
/

BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE incentive CASCADE CONSTRAINTS';
EXCEPTION
   WHEN OTHERS THEN NULL;
END;
/

BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE salary CASCADE CONSTRAINTS';
EXCEPTION
   WHEN OTHERS THEN NULL;
END;
/

BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE state_nationality CASCADE CONSTRAINTS';
EXCEPTION
   WHEN OTHERS THEN NULL;
END;
/

BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE employee CASCADE CONSTRAINTS';
EXCEPTION
   WHEN OTHERS THEN NULL;
END;
/


-- Drop view if exists
BEGIN
   EXECUTE IMMEDIATE 'DROP VIEW e_v';
EXCEPTION
   WHEN OTHERS THEN NULL;
END;
/

-- Create employee table
CREATE TABLE employee (
  emp_id NUMBER(11) PRIMARY KEY,
  name VARCHAR2(100),
  email VARCHAR2(100),
  department VARCHAR2(100),
  designation VARCHAR2(100),
  address VARCHAR2(100),
  contact VARCHAR2(100),
  password VARCHAR2(100),
  reg_date DATE,
  admin NUMBER(11),
  pincode VARCHAR2(10),
  gender VARCHAR2(10),
  dob DATE
);

-- Create sequence and trigger for auto-increment id
CREATE SEQUENCE employee_seq START WITH 11 INCREMENT BY 1;

CREATE OR REPLACE TRIGGER employee_bi
BEFORE INSERT ON employee
FOR EACH ROW
BEGIN
   IF :NEW.emp_id IS NULL THEN
      SELECT employee_seq.NEXTVAL INTO :NEW.emp_id FROM dual;
   END IF;
END;
/

-- Insert data into employee
INSERT INTO employee (emp_id, name, email, department, designation, address, contact, password, reg_date, admin, pincode, gender, dob) VALUES (1,'Yashraj Singh','yashrajsingh4747@gmail.com','everything','owner','MVHR HOSTEL IIITDM KURNOOL','9793960201','rounds=535000$nXFsK3wWLTFfwxUh$vfxqeEEZyhqdjTKbyGJU8HMFlajFteWnNbr1G3Q6/p3',TO_DATE('2018-03-26','YYYY-MM-DD'),1,'143001','male',TO_DATE('2004-05-16','YYYY-MM-DD'));
INSERT INTO employee (emp_id, name, email, department, designation, address, contact, password, reg_date, admin, pincode, gender, dob) VALUES (2,'Prashant Singh','psingh10@gmail.com','Overall','Ceo','bangalore','8095874399','$5$rounds=535000$OO1ZtAds5IaF8RXZ$gp7CyeUX6kTk1HY.4l8xIAA4p158YTuqA7/DWDrXGR8',TO_DATE('2018-03-27','YYYY-MM-DD'),2,'143001','male',TO_DATE('2004-07-10','YYYY-MM-DD'));
-- Continue inserting all other employee rows similarly...

-- Create city_state table
CREATE TABLE city_state (
  city VARCHAR2(100) NOT NULL,
  state VARCHAR2(100) NOT NULL,
  pincode VARCHAR2(10) NOT NULL,
  CONSTRAINT city_state_pk PRIMARY KEY (pincode)
);

-- Insert data into city_state
INSERT INTO city_state VALUES ('Roorkie','Haryana','120124');
INSERT INTO city_state VALUES ('Bihar','Uttar Pradesh','134701');
INSERT INTO city_state VALUES ('Amritsar','Punjab','143001');
INSERT INTO city_state VALUES ('Allahabad','Uttar Pradesh','211012');

-- Create state_nationality table
CREATE TABLE state_nationality (
  state VARCHAR2(100) PRIMARY KEY,
  nationality VARCHAR2(100)
);

INSERT INTO state_nationality VALUES ('Haryana','Indian');
INSERT INTO state_nationality VALUES ('Punjab','Indian');
INSERT INTO state_nationality VALUES ('Uttar Pradesh','Indian');

-- Create attendance table
CREATE TABLE attendance (
  att_date DATE,
  emp_id NUMBER(11),
  CONSTRAINT attendance_fk FOREIGN KEY (emp_id) REFERENCES employee(emp_id)
);

-- Insert data into attendance
INSERT INTO attendance VALUES (TO_DATE('2018-03-28','YYYY-MM-DD'),2);
INSERT INTO attendance VALUES (TO_DATE('2018-03-28','YYYY-MM-DD'),1);
-- Continue inserting other attendance rows...

-- Create incentive table
CREATE TABLE incentive (
  inc_date DATE,
  hours NUMBER(11),
  emp_id NUMBER(11),
  CONSTRAINT incentive_fk FOREIGN KEY (emp_id) REFERENCES employee(emp_id)
);

-- Insert incentive data
INSERT INTO incentive VALUES (TO_DATE('2018-03-28','YYYY-MM-DD'),2,1);
INSERT INTO incentive VALUES (TO_DATE('2018-03-28','YYYY-MM-DD'),12,2);

-- Create salary table
CREATE TABLE salary (
  department VARCHAR2(50),
  designation VARCHAR2(50),
  amount_per_hour NUMBER(11)
);

INSERT INTO salary VALUES ('Overall','Ceo',2000);
INSERT INTO salary VALUES ('Overall','Peon',50);
-- Continue inserting other salary rows...

-- Create view e_v
CREATE OR REPLACE VIEW e_v AS
SELECT e.emp_id, e.name, e.email, e.department, e.designation, e.address, e.contact,
       e.password, e.reg_date, e.admin, e.pincode, e.gender, e.dob,
       cs.state, cs.city, sn.nationality
FROM employee e
LEFT JOIN city_state cs ON e.pincode = cs.pincode
LEFT JOIN state_nationality sn ON cs.state = sn.state;


ALTER TABLE employee MODIFY password VARCHAR2(200);
COMMIT;

UPDATE employee
SET password = '$5$rounds=535000$2lEixgnOGFkICeBH$GALm0I0vqSZYtwFzF8K1TLyunV5P4EjIPXI4KusbLO8'
WHERE emp_id = 1;

UPDATE employee
SET password = '$5$rounds=535000$2lEixgnOGFkICeBH$GALm0I0vqSZYtwFzF8K1TLyunV5P4EjIPXI4KusbLO8'
WHERE emp_id = 2;
commit;

select * from employee;