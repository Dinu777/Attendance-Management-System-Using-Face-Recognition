import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from app.db import get_db
import face_recognition
import _pickle as c
import cv2
import base64
import os
import numpy as np
from datetime import date, datetime
import csv


bp = Blueprint('auth', __name__, url_prefix='/auth')



#----------------------------------------------------------------------------------------------#
#---------------------------------------- Student CURD ----------------------------------------#
#----------------------------------------------------------------------------------------------#



# Student Registeration
@bp.route('/studentRegister', methods=('GET', 'POST'))
def studentRegister():
    if request.method == 'POST':
        name = request.form['name']
        prn = int(request.form['prn'])
        rollNo = int(request.form['rollNo'])
        course = request.form['course']
        year = request.form['year']
        email = request.form['email']
        if request.form['phone'] is not "":
            phone = int(request.form['phone'])
        else: 
            phone = None

        db = get_db()
        error = None


        if db.execute(
            'SELECT rollNo FROM student WHERE prn = ?', (prn,)
        ).fetchone() is not None:
            error = 'prn {} is already registered.'.format(prn)

        if error is None:
            db.execute(
                'INSERT INTO student (prn, name, course, year, rollNo, email, phoneNo) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (prn, name, course, year, rollNo, email, phone)
            )

            db.commit()

            return redirect(url_for('auth.studentFaceRegister', course = course, year = year, prn = prn, **request.args))

        flash(error)

    return render_template('auth/studentRegister.html')

# End of Student Registeration



#  Student Face Registration
@bp.route('/studentFaceRegister', methods=('GET', 'POST'))
def studentFaceRegister():
    if request.method == 'POST':
        photo_base64 = request.form['base64']
        header, encoded = photo_base64.split(",", 1)
        binary_data = base64.b64decode(encoded)
        image_name = "faceData.jpeg"

        with open(os.path.join("app/static/img/capture",image_name), "wb") as f:
            f.write(binary_data)

        
        year = request.args.get('year')
        course = request.args.get('course')
        prn = request.args.get('prn')

        path = f'app/faceDatabase/{course}/{year}'
        img = 'app/static/img/capture/faceData.jpeg'
        prn = str(prn)

        img_array = face_recognition.load_image_file(img)

        try:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
            face_enc = face_recognition.face_encodings(img_array)[0]
            with open(path + "/" + prn, 'wb') as fp:
                c.dump(face_enc, fp)
            
            return redirect(url_for('auth.studentRegister'))

        except:
            flash("face not found")

    return render_template('auth/studentFaceRegister.html')

# End of Student Face Registration



# Student Face Register Transfer route
@bp.route('/studentFaceRegisterTrans', methods=('GET', 'POST'))
def studentFaceRegisterTrans():
    if request.method == 'POST':
        year = request.form['year']
        course = request.form['course']
        prn = request.form['prn']

    return redirect(url_for('auth.studentFaceRegister', course = course, year = year, prn = prn, **request.args))

# End of Student Face Register Transfer route



#  Student Data Read and modify method
@bp.route('/studentCURD', methods=('GET', 'POST'))
def studentCURD():
    
    error = None

    if request.method == 'POST':
        try:
            prn = int(request.form['prn'])
        except:
            flash('Invalid Input')
            return redirect(url_for('auth.studentCURD'))            
        
        db = get_db()
        

        if db.execute(
            'SELECT rollNo FROM student WHERE prn = ?', (prn,)
        ).fetchone() is None:
            error = 'prn {} is not registered.'.format(prn)

        if error is None:
            data = db.execute(
                'SELECT * FROM student WHERE prn = ?', (prn,)
            ).fetchone()

            name = data['name']
            course = data['course']
            year = data['year']
            roll = data['rollNo']
            email = data['email']
            phone = data['phoneNo']

            return render_template('auth/student_view_update_delete.html', prn = data['prn'], name = data['name'], course = data['course'], year = data['year'], roll = data['rollNo'], email = data['email'], phone = data['phoneNo'])

    if error is not None:
        flash(error)

    return render_template('auth/student_view_update_delete.html')

# End of Student Data Read and modify method



# Student Data Delete route
@bp.route('/studentDelete', methods=('GET', 'POST'))
def studentDelete():
    if request.method == 'POST':
        prn = int(request.form['prn'])
        db = get_db()
        data = db.execute(
                'SELECT * FROM student WHERE prn = ?', (prn,)
            ).fetchone()

        course = data['course']
        year = data['year']

        path = f'app/faceDatabase/{course}/{year}/{prn}'

        if os.path.exists(path):
            os.remove(path)

        db.execute(
            'DELETE FROM student WHERE prn= ?', (prn,)
        )
        db.commit()

        return redirect(url_for('admin'))
# End of Student Data Delete route



# Student data edit Transfer Route
@bp.route('/studentEditTrans', methods=('GET', 'POST'))
def studentEditTrans():
    if request.method == 'POST':
        name = request.form['name']
        rollNo = int(request.form['roll'])
        course = request.form['course']
        year = request.form['year']
        email = request.form['email']
        if request.form['phone'] is not "":
            phone = int(request.form['phone'])
        else: 
            phone = None

        db = get_db()
        error = None


        if email is not None or email is not "":
            data = db.execute(
                'SELECT * FROM student WHERE email = ?', (email,)
            ).fetchone()
            prn = data['prn']


        elif phone is not None or phone is not "":
            data = db.execute(
                'SELECT * FROM student WHERE phoneNo = ?', (phone,)
            ).fetchone()
            prn = data['prn']


        if error is None:
            db.execute (
                'UPDATE student SET name = ?, course = ?, year = ?, rollNo = ?, email = ?, phoneNo = ? WHERE prn = ?',
                (name, course, year, rollNo, email, phone, prn)
            )
            db.commit()
            return redirect(url_for('auth.studentCURD'))

        flash(error)

    return redirect(url_for('auth.studentEdit'))

# End of Student data edit Transfer Route



# Student data edit
@bp.route('/studentEdit', methods=('GET', 'POST'))
def studentEdit():
    if request.method == 'POST':
        name = request.form['name']
        rollNo = request.form['roll']
        course = request.form['course']
        year = request.form['year']
        email = request.form['email']
        phone = request.form['phone']

        return render_template('auth/studentEdit.html', name = name, roll = rollNo, email=email, phone = phone, course = course, year = year)

# End of Student data edit



#-----------------------------------------------------------------------------------------------#
#------------------------------------ End of Student Curd --------------------------------------#
#-----------------------------------------------------------------------------------------------#



#----------------------------------------------------------------------------------------------#
#---------------------------------------- Staff CURD ------------------------------------------#
#----------------------------------------------------------------------------------------------#



# Staff Registeration
@bp.route('/staffRegister', methods=('GET', 'POST'))
def staffRegister():
    if request.method == 'POST':
        name = str(request.form['name'])
        role = str(request.form['role'])
        username = str(request.form['username'])
        password = str(request.form['password'])
        subjects = request.form.getlist('subject')
        email = str(request.form['email'])
        try:
            phone = int(request.form['number'])
        except:
            flash('Invalid Phone Number')

            return redirect(url_for('auth.staffRegister'))


        error = None
        db = get_db()

        if role == 'admin':
            if name is "":
                error = 'Name Required'
            
            elif username is "":
                error = 'Username Required'

            elif password is "":
                error = 'Password Required'

            elif email is "":
                error = 'Email ID Required'
            
            elif db.execute(
                'SELECT id FROM staff WHERE name = ?', (name,)
            ).fetchone() is not None:
                error = 'User {} is already registered.'.format(name)
            
            elif db.execute(
                'SELECT id FROM staff WHERE username = ?', (username,)
            ).fetchone() is not None:
                error = 'Username {} is already registered.'.format(username)
            
            elif db.execute(
                'SELECT id FROM staff WHERE email = ?', (email,)
            ).fetchone() is not None:
                error = 'Email {} is already registered.'.format(email)

            elif db.execute(
                'SELECT id FROM staff WHERE phoneNo = ?', (phone,)
            ).fetchone() is not None:
                error = 'Phone No. {} is already registered.'.format(phone)

            
            elif error is None:
                db.execute(
                    'INSERT INTO staff (name, role, username, password, email, phoneNO) VALUES (?, ?, ?, ?, ?, ?)',
                    (name, role,username, generate_password_hash(password), email, phone)
                )

                db.commit()

                return redirect(url_for('auth.staffFaceRegister', name = name, **request.args))



        elif role == 'staff':
            if name is "":
                error = 'Name Required'
            
            elif db.execute(
                'SELECT id FROM staff WHERE name = ?', (name,)
            ).fetchone() is not None:
                error = 'User {} is already registered.'.format(name)
            
            elif db.execute(
                'SELECT id FROM staff WHERE phoneNo = ?', (phone,)
            ).fetchone() is not None:
                error = 'Phone No. {} is already registered.'.format(phone)

            elif error is None:
                db.execute(
                    'INSERT INTO staff (name, role, phoneNO) VALUES (?, ?, ?)',
                    (name, role, phone)
                )

                db.commit()

                return redirect(url_for('auth.staffFaceRegister', name = name, **request.args))



        elif role == 'faculty':
            if name is "":
                error = 'Name Required'
            
            elif username is "":
                error = 'Username Required'

            elif password is "":
                error = 'Password Required'

            elif phone is "":
                error = 'Phone No. Required'

            elif email is "":
                error = 'Email ID Required'

            elif len(subjects) == 0:
                error = 'Subject Required'
            
            elif db.execute(
                'SELECT id FROM staff WHERE name = ?', (name,)
            ).fetchone() is not None:
                error = 'User {} is already registered.'.format(name)
            
            elif db.execute(
                'SELECT id FROM staff WHERE email = ?', (email,)
            ).fetchone() is not None:
                error = 'Email {} is already registered.'.format(email)

            elif db.execute(
                'SELECT id FROM staff WHERE username = ?', (username,)
            ).fetchone() is not None:
                error = '{} is already registered.'.format(username)

            elif error is None:
                db.execute(
                    'INSERT INTO staff (name, role, username, password, subjects, email, phoneNO) VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (name, role,username, generate_password_hash(password), str(subjects), email, phone)
                )

                db.commit()

                return redirect(url_for('auth.staffFaceRegister', name = name, **request.args))

        
        flash(error)
        
    return render_template('auth/staffRegister.html', subject = subjectData())

# End of Staff Registeration



# Subject data retrival
def subjectData():
    db = get_db()

    subjectData = db.execute(
            'SELECT subject FROM subjects'
    )

    subject = []
    for data in subjectData:
        subject.append(data[0])

    return subject

# End of subject Data Retrival



#  Staff Face Registration
@bp.route('/staffFaceRegister', methods=('GET', 'POST'))
def staffFaceRegister():
    if request.method == 'POST':
        photo_base64 = request.form['base64']
        header, encoded = photo_base64.split(",", 1)
        binary_data = base64.b64decode(encoded)
        image_name = "faceData.jpeg"

        with open(os.path.join("app/static/img/capture",image_name), "wb") as f:
            f.write(binary_data)


        name = str(request.args.get('name'))

        path = 'app/faceDatabase/staff'
        img = 'app/static/img/capture/faceData.jpeg'

        img_array = face_recognition.load_image_file(img)

        try:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
            face_enc = face_recognition.face_encodings(img_array)[0]
            with open(path + "/" + name, 'wb') as fp:
                c.dump(face_enc, fp)
            
            return redirect(url_for('auth.staffRegister'))

        except:
            flash("face not found")

    return render_template('auth/staffFaceRegister.html')

# End of Staff Face Registration



# Staff Face Edit Transfer Route
@bp.route('/staffFaceRegisterTrans', methods=('GET', 'POST'))
def staffFaceRegisterTrans():
    if request.method == 'POST':
        name = request.form['name']

    return redirect(url_for('auth.staffFaceRegister', name = name, **request.args))

# End of Staff Face Edit Transfer Route



# Staff Data Read and modify method
@bp.route('/staffCURD', methods=('GET', 'POST'))
def staffCURD():
    error = None

    if request.method == 'POST':
        
        name = request.form['name']
        
        db = get_db()
        
        if db.execute(
            'SELECT id FROM staff WHERE name = ?', (name,)
        ).fetchone() is None:
            error = 'Name {} is not registered.'.format(name)

        if error is None:
            data = db.execute(
                'SELECT * FROM staff WHERE name = ?', (name,)
            ).fetchone()

            subjectStr = data['subjects']
            if subjectStr is not None:
                subjectLst = subjectStr.strip('][').split(', ') 
                subject = []
                for i in subjectLst:
                    subject.append(i[1:-1])

                return render_template('auth/staff_view_update_delete.html', role = data['role'], name = data['name'], username = data['username'], subjects = subject, email = data['email'], phone = data['phoneNo'])

            return render_template('auth/staff_view_update_delete.html', role = data['role'], name = data['name'], username = data['username'], email = data['email'], phone = data['phoneNo'])


    if error is not None:
        flash(error)
        
    return render_template('auth/staff_view_update_delete.html')

# End of Staff Data Read and modify method



# Staff Data Edit
@bp.route('/staffEdit', methods=('GET', 'POST'))
def staffEdit():
    if request.method == 'POST':
        name = request.form['name']
        role = request.form['role']
        username = request.form['username']
        subject = request.form.getlist('subject')
        email = request.form['email']
        phone = request.form['phone']

        if role == 'staff':
            flash("Staff Data Can't be Edited")
            return redirect(url_for('auth.staffCURD'))

        elif role == 'admin':
            return render_template('auth/staffEdit.html', name = name,role=role, email=email, phone = phone, username = username)

        elif role == 'faculty':
            return render_template('auth/staffEdit.html', name = name, role=role, email=email, phone = phone, username = username, subjects = subject, subjectlist = subjectData())

# End of Staff Data Edit



# Staff Data Edit Transfer Route
@bp.route('/staffEditTrans', methods=('GET', 'POST'))
def staffEditTrans():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        subject = request.form.getlist('subject')
        email = request.form['email']
        if request.form['phone'] is not "":
            phone = int(request.form['phone'])
        else: 
            phone = None

        db = get_db()
        error = None

        if email is not None or email is not "":
            data = db.execute(
                'SELECT * FROM staff WHERE email = ?', (email,)
            ).fetchone()

            role = data['role']
            prev_name = data['name']


        elif phone is not None or phone is not "":
            data = db.execute(
                'SELECT * FROM staff WHERE phoneNo = ?', (phone,)
            ).fetchone()

            role = data['role']
            prev_name = data['name']

        if error is None:
            if role == 'admin':
                db.execute (
                    'UPDATE staff SET name = ?, username = ?, password = ?, email = ?, phoneNo = ? WHERE name = ?',
                    (name, username, generate_password_hash(password), email, phone, prev_name)
                )

                db.commit()

                if name != prev_name:
                    os.rename(f'faceDatabase/staff/{prev_name}', f'faceDatabase/staff/{name}')

                return redirect(url_for('auth.staffCURD'))

            elif role == 'faculty':
                db.execute (
                    'UPDATE staff SET name = ?, username = ?, password = ?,subjects = ?, email = ?, phoneNo = ? WHERE name = ?',
                    (name, username, generate_password_hash(password),str(subject), email, phone, prev_name)
                )

                db.commit()
                
                if name != prev_name:
                    os.rename(f'app/faceDatabase/staff/{prev_name}', f'app/faceDatabase/staff/{name}')

                return redirect(url_for('auth.staffCURD'))
            
        flash(error)

    return redirect(url_for('auth.studentEdit'))

# End of Staff Data Edit Transfer Route



# Staff Data Delete
@bp.route('/staffDelete', methods=('GET', 'POST'))
def staffDelete():
    if request.method == 'POST':
        name = request.form['name']
        db = get_db()

        path = f'app/faceDatabase/staff/{name}'

        if os.path.exists(path):
            os.remove(path)

        db.execute(
            'DELETE FROM staff WHERE name= ?', (name,)
        )

        db.commit()

        return redirect(url_for('admin'))

# End of Staff Data Delete



#-----------------------------------------------------------------------------------------------#
#------------------------------------ End of Staff Curd ----------------------------------------#
#-----------------------------------------------------------------------------------------------#



#-----------------------------------------------------------------------------------------------#
#------------------------------------ Student Attendance ---------------------------------------#
#-----------------------------------------------------------------------------------------------#



# Student Data Retrival
def studentList(course, year):
    db = get_db()

    studentData = db.execute(
            'SELECT name FROM student WHERE course = ? AND year = ?', (course, year)
    )

    student = []

    for data in studentData:
        student.append(data[0])

    return student

# End of Student Data Retrival



# Student Attendance Transfer route
@bp.route('/studentAttendanceTrans/<name>/<subjectStr>', methods=('GET', 'POST'))
def studentAttendanceTrans(name, subjectStr):
    if subjectStr is not None:
        subjectLst = subjectStr.strip('][').split(', ') 

        subject = []
        
        for i in subjectLst:
            subject.append(i[1:-1])

    return render_template('studentAttendance.html', name = name, subject = subject)

# End of Student Attendance Transfer route



# Student Attendance Page render with Data
@bp.route('/studentAttendance', methods=('GET', 'POST'))
def studentAttendance():
    if request.method == "POST":
        name = request.form['name']
        subject = request.form['subject']

        db = get_db()

        subjectData = db.execute(
                    'SELECT * FROM subjects WHERE subject = ?', (subject,)
        ).fetchone()

        course = subjectData['course']
        year = subjectData['year']

        student = studentList(course, year)

        return render_template("detect.html", name = name, subject=subject, course = course, year = year, students = student)

# End of Student Attendance Page render with Data



# Detect Student Face and Mark Attendance in file
@bp.route('/detect', methods=('GET', 'POST'))
def detect():
    
    faces = []
    faceName = []

    if request.method == 'POST':
        photo_base64 = request.form['base64']
        faculty_name = request.form['name']
        subject = request.form['subject']
        course = request.form['course']
        year = request.form['year']
        studentMarked = request.form.getlist('student')

        student = studentList(course, year)

        if photo_base64 != None and photo_base64 != "":

            # Unload Face Encoding
            path = f'app/faceDatabase/{course}/{year}'
            myList = os.listdir(path)
            for x, cl in enumerate(myList):
                with open(path + "/" + cl, 'rb') as fp: 
                    face_info = c.load(fp)

                faces.append(face_info)
                faceName.append(cl)

            # Image Processing
            header, encoded = photo_base64.split(",", 1)
            binary_data = base64.b64decode(encoded)
            image_name = "faceData.jpeg"

            with open(os.path.join("app/static/img/capture",image_name), "wb") as f:
                f.write(binary_data)

            # Detection
            img = cv2.imread('app/static/img/capture/faceData.jpeg', cv2.IMREAD_COLOR)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            facesCurFrame = face_recognition.face_locations(img)
            encodesCurFrame = face_recognition.face_encodings(img, facesCurFrame)

            for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                
                matches = face_recognition.compare_faces(faces, encodeFace)
                faceDis = face_recognition.face_distance(faces, encodeFace)
                
                matchIndex = np.argmin(faceDis)
                
                if matches[matchIndex]:
                    prn = faceName[matchIndex].upper()

                    db = get_db()

                    subjectData = db.execute(
                            'SELECT * FROM student WHERE prn = ?', (prn,)
                        ).fetchone()

                    studentMarked.append(subjectData['name'])

            return render_template('detect.html', name = faculty_name, subject = subject, course = course, year = year, students = student, studentMarked = studentMarked)


        else:
            if len(studentMarked) == 0:
                return render_template('detect.html', name = faculty_name, subject = subject, course = course, year = year, students = student, studentMarked = studentMarked)

            else:
                today = date.today()
                attendace_path = f'app/attendance/student/{course}/{year}'
                if not os.path.exists(os.path.join(attendace_path, f'{today.strftime("%Y-%m-%d")}.csv')):
                    
                    with open(os.path.join(attendace_path, f'{today.strftime("%Y-%m-%d")}.csv'), 'w+') as csvfile:
                        filewriter = csv.writer(csvfile)
                        filewriter.writerow(['Name',subject])
                        
                        for name in student:
                            if name in studentMarked:
                                filewriter.writerow([name,1])

                            else:
                                filewriter.writerow([name,0])

                else:
                    update = []

                    fhandler = open(os.path.join(attendace_path, f'{today.strftime("%Y-%m-%d")}.csv'), "r") 
                    freader = fhandler.readlines()

                    leng = len(freader[0].split(','))
                    header = freader[0].split(',')
                    header[leng - 1] = header[leng - 1][:-1]
                    header.append(subject)

                    update.append(header)

                    for i in freader[1:]:
                        i = i.split(',')
                        i[leng - 1] = i[leng - 1][:-1]

                        if i[0] in studentMarked:
                            i.append('1')

                        else:
                            i.append('0')

                        update.append(i)
                    
                    fhandler.close()

                    with open(os.path.join(attendace_path, f'{today.strftime("%Y-%m-%d")}.csv'), 'w+') as file:
                        filewriter = csv.writer(file)

                        for i in update:
                            filewriter.writerow(i)

                return redirect(url_for('auth.logout'))

    return render_template('detect.html', name = faculty_name, subject = subject, course = course, year = year, students = student, studentMarked = studentMarked)

# End of Detect Student Face and Mark Attendance in file



#-----------------------------------------------------------------------------------------------#
#--------------------------------- End of Student Attendance -----------------------------------#
#-----------------------------------------------------------------------------------------------#



#-----------------------------------------------------------------------------------------------#
#-------------------------------------- Staff Attendance ---------------------------------------#
#-----------------------------------------------------------------------------------------------#



# Detect Staff Face and Mark Attendance in file
@bp.route('/staffAttendance', methods=('GET', 'POST'))
def staffAttendance():
    faces = []
    faceName = []

    # Unload Face Encoding
    path = 'app/faceDatabase/staff'
    myList = os.listdir(path)

    for x, cl in enumerate(myList):
        with open(path + "/" + cl, 'rb') as fp: 
            face_info = c.load(fp)

        faces.append(face_info)
        faceName.append(cl)

    if request.method == 'POST':
        photo_base64 = request.form['base64']

        if photo_base64 != None and photo_base64 != "":
            # Image Processing
            header, encoded = photo_base64.split(",", 1)
            binary_data = base64.b64decode(encoded)
            image_name = "faceData.jpeg"

            with open(os.path.join("app/static/img/capture",image_name), "wb") as f:
                f.write(binary_data)

            # Detection
            img = cv2.imread('app/static/img/capture/faceData.jpeg', cv2.IMREAD_COLOR)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            facesCurFrame = face_recognition.face_locations(img)
            encodesCurFrame = face_recognition.face_encodings(img, facesCurFrame)

            for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                
                matches = face_recognition.compare_faces(faces, encodeFace)
                faceDis = face_recognition.face_distance(faces, encodeFace)
                
                matchIndex = np.argmin(faceDis)
                
                if matches[matchIndex]:
                    name = faceName[matchIndex]

                    # Mark Attendance
                    today = date.today()
                    now = datetime.now()
                    attendace_path = f'app/attendance/staff'
                    
                    if not os.path.exists(os.path.join(attendace_path, f'{today.strftime("%Y-%m-%d")}.csv')):
                        with open(os.path.join(attendace_path, f'{today.strftime("%Y-%m-%d")}.csv'), 'w+') as csvfile:
                            filewriter = csv.writer(csvfile)
                            filewriter.writerow(['Name','IN-Time', 'OUT-Time'])
                            filewriter.writerow([name,now.strftime("%H:%M:%S")])

                    else:
                        fhandler = open(os.path.join(attendace_path, f'{today.strftime("%Y-%m-%d")}.csv'), "r") 
                        freader = fhandler.readlines() 

                        update = []
                        name_in_file = []

                        update.append(freader[0][:-1].split(','))

                        for i in freader[1:]:
                            i = i.split(',')
                            name_in_file.append(i[0])

                        if name in name_in_file:
                            for i in freader[1:]:
                                i = i.split(',')
                                i[len(i) - 1] = i[len(i) - 1][:-1]

                                if i[0] in name_in_file:                                    
                                    if len(i) < 3:
                                        i.append(now.strftime("%H:%M:%S"))
                                        update.append(i)
                                    
                                    else:
                                        i[2] = now.strftime("%H:%M:%S")
                                        update.append(i)
                                
                        else:
                            update.append([name, now.strftime("%H:%M:%S")])
                    
                        fhandler.close()

                        with open(os.path.join(attendace_path, f'{today.strftime("%Y-%m-%d")}.csv'), 'w+') as file:
                            filewriter = csv.writer(file)
                            
                            for i in update:
                                filewriter.writerow(i)

                    return render_template('staffAttendanceResult.html', name = name)

                else:
                    print('face not found')

        else:
            print("Capture, Save and Submit Image")
            
    return render_template('staffAttendance.html')

# End of Detect Staff Face and Mark Attendance in file



#-----------------------------------------------------------------------------------------------#
#----------------------------------- End of Staff Attendance -----------------------------------#
#-----------------------------------------------------------------------------------------------#



#-----------------------------------------------------------------------------------------------#
#--------------------------------------- Login System ------------------------------------------#
#-----------------------------------------------------------------------------------------------#



# Login Function
@bp.route('/login', methods=('GET', 'POST'))
def login():
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        error = None
        
        user = db.execute(
            'SELECT * FROM staff WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        elif error is None:
            session.clear()
            session['user_id'] = user['id']
            
            if user['role'] == 'admin':
                return redirect(url_for('admin'))
            
            elif user['role'] == 'faculty':
                name = user['name']
                subjectStr = user['subjects']
                
                if subjectStr is not None:
                    subjectLst = subjectStr.strip('][').split(', ') 
                    subject = []
                    
                    for i in subjectLst:
                        subject.append(i[1:-1])
                
                return redirect(f'/auth/studentAttendanceTrans/{name}/{subject}')

        flash(error)

    return render_template('auth/login.html')

# End of Login Function



# Logged in user Session creation
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    
    else:
        g.user = get_db().execute(
            'SELECT * FROM staff WHERE id = ?', (user_id,)
        ).fetchone()

# End of Logged in user Session creation



# Logout Function
@bp.route('/logout')
def logout():
    session.clear()
    
    return redirect(url_for('auth.login'))

# End of Logout Function



# Page login required function
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

# End of Page login required function



#-----------------------------------------------------------------------------------------------#
#------------------------------------- End of Login System -------------------------------------#
#-----------------------------------------------------------------------------------------------#