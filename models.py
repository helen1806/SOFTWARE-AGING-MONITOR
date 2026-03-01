from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Website(db.Model):
    __tablename__ = 'websites'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(500), nullable=False, unique=True)
    monitoring_interval = db.Column(db.Integer, default=1)
    response_threshold = db.Column(db.Integer, default=5000)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    checks = db.relationship('MonitoringCheck', backref='website', lazy='dynamic', cascade='all, delete-orphan')
    incidents = db.relationship('Incident', backref='website', lazy='dynamic', cascade='all, delete-orphan')

class MonitoringCheck(db.Model):
    __tablename__ = 'monitoring_checks'
    
    id = db.Column(db.Integer, primary_key=True)
    website_id = db.Column(db.Integer, db.ForeignKey('websites.id'), nullable=False)
    status_code = db.Column(db.Integer)
    response_time = db.Column(db.Float)
    is_up = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text)
    checked_at = db.Column(db.DateTime, default=datetime.utcnow)

class Incident(db.Model):
    __tablename__ = 'incidents'
    
    id = db.Column(db.Integer, primary_key=True)
    website_id = db.Column(db.Integer, db.ForeignKey('websites.id'), nullable=False)
    incident_type = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.String(20), default='warning')
    description = db.Column(db.Text)
    probable_cause = db.Column(db.Text)
    suggestion = db.Column(db.Text)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)
    duration_seconds = db.Column(db.Integer)
    is_resolved = db.Column(db.Boolean, default=False)

class SubPage(db.Model):
    __tablename__ = 'subpages'
    
    id = db.Column(db.Integer, primary_key=True)
    website_id = db.Column(db.Integer, db.ForeignKey('websites.id'), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    name = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    
    website = db.relationship('Website', backref=db.backref('subpages', lazy='dynamic', cascade='all, delete-orphan'))
