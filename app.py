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

