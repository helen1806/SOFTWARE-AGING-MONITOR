import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from models import db, Website, MonitoringCheck, Incident, SubPage
from monitor import monitor_website, get_website_stats

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production') 
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Root@localhost:5433/Software aging'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app) ##database successfuly connected to db

scheduler = BackgroundScheduler()
scheduler_started = False

def start_scheduler():
    global scheduler_started
    if not scheduler_started:
        scheduler.start()
        scheduler_started = True
        schedule_all_monitors() #run this function

def schedule_all_monitors():
    for job in scheduler.get_jobs():
        job.remove()
    
    with app.app_context():##TEMPORARILY WORK THIS APP
        websites = Website.query.filter_by(is_active=True).all()
        for website in websites:
            scheduler.add_job(
                func=monitor_website, ##REPEAT THIS FUNCTION
                trigger='interval',
                minutes=website.monitoring_interval,
                args=[app, website.id],
                id=f'monitor_{website.id}',
                replace_existing=True
            )

@app.route('/')
def dashboard():
    websites = Website.query.all()
    website_data = []
    
    for website in websites:
        last_check = MonitoringCheck.query.filter_by(website_id=website.id).order_by(MonitoringCheck.checked_at.desc()).first()
        active_incidents = Incident.query.filter_by(website_id=website.id, is_resolved=False).count()
        stats = get_website_stats(website.id, 'day')
        
        website_data.append({
            'website': website,
            'last_check': last_check,
            'active_incidents': active_incidents,
            'stats': stats
        })
    
    return render_template('dashboard.html', websites=website_data)


@app.route('/website/<int:id>') #website id
def website_detail(id):
    website = Website.query.get_or_404(id) #if id not receieved ,show error 404 
    period = request.args.get('period', 'day')
    stats = get_website_stats(id, period)
    
    now = datetime.utcnow()
    if period == 'day':
        start_time = now - timedelta(days=1)
    elif period == 'week':
        start_time = now - timedelta(weeks=1)
    elif period == 'month':
        start_time = now - timedelta(days=30)
    else:
        start_time = now - timedelta(days=365)
    
    checks = MonitoringCheck.query.filter(
        MonitoringCheck.website_id == id,
        MonitoringCheck.checked_at >= start_time
    ).order_by(MonitoringCheck.checked_at.desc()).limit(100).all()
    
    incidents = Incident.query.filter(
        Incident.website_id == id,
        Incident.started_at >= start_time
    ).order_by(Incident.started_at.desc()).all()
    
    subpages = website.subpages.all()
    
    return render_template('website_detail.html', 
                         website=website, 
                         stats=stats, 
                         checks=checks, 
                         incidents=incidents,
                         subpages=subpages,
                         period=period)


@app.route('/reports')
def reports():
    websites = Website.query.all()
    return render_template('reports.html', websites=websites)

@app.route('/api/report/<int:website_id>')
def generate_report(website_id):
    period = request.args.get('period', 'week')
    website = Website.query.get_or_404(website_id)
    stats = get_website_stats(website_id, period)
    
    now = datetime.utcnow()
    if period == 'week':
        start_time = now - timedelta(weeks=1)
    elif period == 'month':
        start_time = now - timedelta(days=30)
    else:
        start_time = now - timedelta(days=365)
    
    incidents = Incident.query.filter(
        Incident.website_id == website_id,
        Incident.started_at >= start_time
    ).order_by(Incident.started_at.desc()).all()
    
    checks = MonitoringCheck.query.filter(
        MonitoringCheck.website_id == website_id,
        MonitoringCheck.checked_at >= start_time
    ).all()
    
    incident_data = []
    for inc in incidents:
        incident_data.append({
            'type': inc.incident_type,
            'severity': inc.severity,
            'description': inc.description,
            'cause': inc.probable_cause,
            'suggestion': inc.suggestion,
            'started_at': inc.started_at.isoformat(),
            'ended_at': inc.ended_at.isoformat() if inc.ended_at else None,
            'duration': inc.duration_seconds,
            'resolved': inc.is_resolved
        })
    
    response_times = [c.response_time for c in checks if c.response_time]
    
    return jsonify({
        'website': website.name,
        'url': website.url,
        'period': period,
        'generated_at': datetime.utcnow().isoformat(),
        'stats': stats,
        'incidents': incident_data,
        'response_time_data': {
            'min': min(response_times) if response_times else 0,
            'max': max(response_times) if response_times else 0,
            'avg': sum(response_times) / len(response_times) if response_times else 0
        }
    })

