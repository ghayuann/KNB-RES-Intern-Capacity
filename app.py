from flask import Flask, render_template, request, jsonify
from models import db, Intern, Project
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///intern_capacity.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Predefined list of supervisors for dropdown
FULL_TIME_STAFF = ["See Ping, Tan", "RuiXi, Seet", "Ryan, Surayan", "Jason, Foo"]

@app.before_request
def create_tables():
    db.create_all()

# ✅ Main Dashboard
@app.route('/')
def dashboard():
    interns = Intern.query.all()
    return render_template('dashboard.html', interns=interns, staff_list=FULL_TIME_STAFF)

# ✅ Add Intern
@app.route('/add_intern', methods=['POST'])
def add_intern():
    name = request.form['name']
    intern = Intern(name=name)
    db.session.add(intern)
    db.session.commit()
    return jsonify({'status': 'success', 'id': intern.id, 'name': intern.name})

# ✅ Assign Project with stakeholder & deadline
@app.route('/assign_project', methods=['POST'])
def assign_project():
    intern_id = request.form['intern_id']
    project_name = request.form['project_name']
    assigned_by = request.form['assigned_by']
    stakeholder = request.form['stakeholder']
    deadline = request.form.get('deadline')

    deadline_date = None
    if deadline:
        deadline_date = datetime.strptime(deadline, "%Y-%m-%d").date()

    intern = Intern.query.get(intern_id)
    if not intern:
        return jsonify({'status': 'error', 'message': 'Intern not found'}), 404

    project = Project(
        project_name=project_name,
        assigned_by=assigned_by,
        stakeholder=stakeholder,
        deadline=deadline_date,
        intern_id=intern_id,
        status='Active'
    )
    db.session.add(project)
    db.session.commit()

    return jsonify({
        'status': 'success',
        'id': project.id,
        'name': project.project_name,
        'supervisor': project.assigned_by,
        'stakeholder': stakeholder,
        'deadline': str(deadline_date) if deadline_date else None
    })

# ✅ Complete Project
@app.route('/complete_project/<int:id>', methods=['POST'])
def complete_project(id):
    project = Project.query.get(id)
    if project and project.status == 'Active':
        project.status = 'Completed'
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'}), 404

# ✅ Delete Intern
@app.route('/delete_intern/<int:id>', methods=['POST'])
def delete_intern(id):
    intern = Intern.query.get(id)
    if intern:
        Project.query.filter_by(intern_id=id).delete()
        db.session.delete(intern)
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'}), 404

# ✅ Delete Project
@app.route('/delete_project/<int:id>', methods=['POST'])
def delete_project(id):
    project = Project.query.get(id)
    if project:
        db.session.delete(project)
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'}), 404

# ✅ Edit Intern Name
@app.route('/edit_intern/<int:id>', methods=['POST'])
def edit_intern(id):
    intern = Intern.query.get(id)
    if intern:
        intern.name = request.form['name']
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'}), 404

# ✅ Edit Project Name
@app.route('/edit_project/<int:id>', methods=['POST'])
def edit_project(id):
    project = Project.query.get(id)
    if project:
        project.project_name = request.form['project_name']
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'}), 404

# ✅ Get updated capacity score (AJAX)
@app.route('/get_capacity_score/<int:id>')
def get_capacity_score(id):
    intern = Intern.query.get(id)
    if intern:
        return jsonify({'score': intern.capacity_score(), 'max_capacity': intern.max_capacity})
    return jsonify({'error': 'Intern not found'}), 404

# ✅ Get Summary for all interns (AJAX)
@app.route('/get_summary')
def get_summary():
    interns = Intern.query.all()
    data = []
    for intern in interns:
        data.append({
            'id': intern.id,
            'name': intern.name,
            'score': intern.capacity_score(),
            'max_capacity': intern.max_capacity,
            'projects': [
                {
                    'name': p.project_name,
                    'capacity': p.project_capacity(),
                    'stakeholder': p.stakeholder  # ✅ Added this so JS can color by stakeholder
                }
                for p in intern.projects if p.status == 'Active'
            ]
        })
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
