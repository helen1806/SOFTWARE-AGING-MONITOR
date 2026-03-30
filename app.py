import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from models import db, Website, MonitoringCheck, Incident, SubPage
from monitor import monitor_website, get_website_stats
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production') 
app.config['SQLALCHEMY_DATABASE_URI'] =os.environ.get('DATABASE_URL')
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


@app.route('/api/websites', methods=['GET', 'POST'])
def api_websites():
    if request.method == 'POST':
        data = request.json
        website = Website(
            name=data['name'],
            url=data['url'],
            monitoring_interval=data.get('monitoring_interval', 1),
            response_threshold=data.get('response_threshold', 5000)
        )
        db.session.add(website)
        db.session.commit()
        
        if scheduler_started:
            scheduler.add_job(
                func=monitor_website,
                trigger='interval',
                minutes=website.monitoring_interval,
                args=[app, website.id],
                id=f'monitor_{website.id}',
                replace_existing=True
            )
            monitor_website(app, website.id)
        
        return jsonify({'id': website.id, 'message': 'Website added successfully'})
    
    websites = Website.query.all()
    return jsonify([{
        'id': w.id,
        'name': w.name,
        'url': w.url,
        'monitoring_interval': w.monitoring_interval,
        'is_active': w.is_active
    } for w in websites])

@app.route('/api/websites/<int:id>', methods=['DELETE', 'PUT'])
def api_website(id):
    website = Website.query.get_or_404(id)
    
    if request.method == 'DELETE':
        if scheduler_started:
            try:
                scheduler.remove_job(f'monitor_{id}')
            except:
                pass
        db.session.delete(website)
        db.session.commit()
        return jsonify({'message': 'Website deleted'})
    
    if request.method == 'PUT':
        data = request.json
        website.name = data.get('name', website.name)
        website.url = data.get('url', website.url)
        website.monitoring_interval = data.get('monitoring_interval', website.monitoring_interval)
        website.response_threshold = data.get('response_threshold', website.response_threshold)
        website.is_active = data.get('is_active', website.is_active)
        db.session.commit()
        
        if scheduler_started:
            try:
                scheduler.remove_job(f'monitor_{id}')
            except:
                pass
            if website.is_active:
                scheduler.add_job(
                    func=monitor_website,
                    trigger='interval',
                    minutes=website.monitoring_interval,
                    args=[app, website.id],
                    id=f'monitor_{id}',
                    replace_existing=True
                )
        
        return jsonify({'message': 'Website updated'})

@app.route('/api/websites/<int:id>/subpages', methods=['GET', 'POST'])
def api_subpages(id):
    website = Website.query.get_or_404(id)
    
    if request.method == 'POST':
        data = request.json
        subpage = SubPage(
            website_id=id,
            url=data['url'],
            name=data.get('name', '')
        )
        db.session.add(subpage)
        db.session.commit()
        return jsonify({'id': subpage.id, 'message': 'Subpage added'})
    
    subpages = website.subpages.all()
    return jsonify([{
        'id': s.id,
        'url': s.url,
        'name': s.name,
        'is_active': s.is_active
    } for s in subpages])

@app.route('/api/subpages/<int:id>', methods=['DELETE'])
def api_subpage(id):
    subpage = SubPage.query.get_or_404(id)
    db.session.delete(subpage)
    db.session.commit()
    return jsonify({'message': 'Subpage deleted'})

@app.route('/api/check/<int:website_id>')
def trigger_check(website_id):
    monitor_website(app, website_id)
    return jsonify({'message': 'Check triggered'})

@app.route('/api/chart-data/<int:website_id>')
def chart_data(website_id):
    period = request.args.get('period', 'day')
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
        MonitoringCheck.website_id == website_id,
        MonitoringCheck.checked_at >= start_time
    ).order_by(MonitoringCheck.checked_at.asc()).all()
    
    return jsonify({
        'labels': [c.checked_at.strftime('%Y-%m-%d %H:%M') for c in checks],
        'response_times': [c.response_time if c.response_time else 0 for c in checks],
        'status': [1 if c.is_up else 0 for c in checks]
    })

with app.app_context():
    db.create_all()

if __name__ == '__main__': 
    start_scheduler()
    app.run(host='0.0.0.0', port=5000, debug=True)

