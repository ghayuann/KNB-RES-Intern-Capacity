from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Define stakeholder importance weights
STAKEHOLDER_WEIGHTS = {
    "Government": 7,
    "Board of Directors": 6,
    "EXCO": 5,
    "IC": 4,
    "Investors Request": 3,
    "Public Markets": 2,
    "Misc": 1
}

class Intern(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    max_capacity = db.Column(db.Integer, default=35)  # Represents weighted capacity
    projects = db.relationship('Project', backref='intern', lazy=True)

    def current_load(self):
        """Returns count of active projects."""
        return len([p for p in self.projects if p.status == 'Active'])

    def capacity_score(self):
        """Calculates weighted capacity score = importance × urgency."""
        today = datetime.today().date()
        score = 0
        for project in self.projects:
            if project.status == 'Active':
                importance = STAKEHOLDER_WEIGHTS.get(project.stakeholder, 1)
                urgency = 1
                if project.deadline:
                    days_left = (project.deadline - today).days
                    if days_left <= 7:
                        urgency = 10
                    elif days_left <= 14:
                        urgency = 9
                    elif days_left <= 30:
                        urgency = 7
                    elif days_left <= 60:
                        urgency = 3
                    else:
                        urgency = 1
                score += importance * urgency
        return score

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(200), nullable=False)
    assigned_by = db.Column(db.String(100), nullable=False)
    stakeholder = db.Column(db.String(50), nullable=False)
    deadline = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), default='Active')
    intern_id = db.Column(db.Integer, db.ForeignKey('intern.id'), nullable=False)

    def project_capacity(self):
        """Calculates capacity contribution of a single project."""
        today = datetime.today().date()
        importance = STAKEHOLDER_WEIGHTS.get(self.stakeholder, 1)

        urgency = 1
        if self.deadline:
            days_left = (self.deadline - today).days
            if days_left <= 7:
                urgency = 10
            elif days_left <= 14:
                urgency = 9
            elif days_left <= 30:
                urgency = 7
            elif days_left <= 60:
                urgency = 3
            else:
                urgency = 1

        return importance * urgency
