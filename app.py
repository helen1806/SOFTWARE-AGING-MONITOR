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
