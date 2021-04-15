import os
from flask import Flask, render_template, request, url_for, redirect, send_file, flash



def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'app.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    from . import db, auth
    db.init_app(app)

    app.register_blueprint(auth.bp)


    @app.route("/")
    def startWindow():
        return render_template("startWindow.html")

    @app.route("/home")
    def home():
        return render_template("home.html")

    @app.route("/admin")
    def admin():
        return render_template("admin.html")

    
    @app.route("/about")
    def about():
        return render_template("about2.html")

    @app.route('/download', methods=('GET', 'POST'))
    def download():
        if request.method == 'POST':
            date = str(request.form['date'])
            course = request.form['course']
            year = request.form['year']

            # print(date)
            # print(course)
            # print(year)

            try:
                if course == 'staff':
                    return send_file(f'attendance/{course}/{date}.csv',
                            mimetype='text/csv',
                            attachment_filename=f'{date}-staff.csv',
                            as_attachment=True)
                
                else:
                    return send_file(f'attendance/student/{course}/{year}/{date}.csv',
                        mimetype='text/csv',
                        attachment_filename=f'{date}-student-{year}-{course}.csv',
                        as_attachment=True)
            except:
                flash('File Not Found')
                flash('Possible cause:')
                flash('1. Holiday')
                flash('2. Attendance Not taken')
                flash('3. File Deleted')

        return redirect(url_for('home'))


    return app
