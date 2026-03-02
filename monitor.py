import requests
from datetime import datetime, timedelta
from models import db, Website,MonitoringCheck,Incident,SubPage
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

INCIDENT_TYPES = {
    
    'timeout': {
        'cause': 'Server not responding within expected timeframe',
        'suggestion': 'Check server resources, network connectivity, and consider scaling infrastructure'
    },
    
    'slow_response': {
        'cause': 'High server load, database bottlenecks, or network latency',
        'suggestion': 'Optimize database queries, enable caching, check server CPU/memory usage'
    },
    'server_error': {
        'cause': 'Internal server error, application crash, or configuration issue',
        'suggestion': 'Review server logs, check application health, verify configurations'
    },
    'connection_error': {
        'cause': 'Network connectivity issues or server unreachable',
        'suggestion': 'Verify DNS settings, check firewall rules, confirm server is running'
    },
    'client_error': {
        'cause': 'Resource not found, unauthorized access, or bad request',
        'suggestion': 'Verify URL paths, check authentication settings, review request format'
    },
    'ssl_error': {
        'cause': 'SSL certificate expired or invalid',
        'suggestion': 'Renew SSL certificate, verify certificate chain, check domain configuration'
    }
}



def check_url(url, timeout=30): #check if the website is working
    try:
        start_time = datetime.now()
        response = requests.get(url, timeout=timeout, allow_redirects=True, 
                              headers={'User-Agent': 'SoftwareAgingMonitor/1.0'})
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds() * 1000
        
        return {
            'status_code': response.status_code,
            'response_time': response_time,
            'is_up': 200 <= response.status_code < 400,
            'error_message': None
        }
    except requests.exceptions.Timeout:
        return {
            'status_code': None,
            'response_time': timeout * 1000,
            'is_up': False,
            'error_message': 'Request timeout'
        }
    except requests.exceptions.SSLError as e:
        return {
            'status_code': None,
            'response_time': None,
            'is_up': False,
            'error_message': f'SSL Error: {str(e)}'
        }
    

    except requests.exceptions.ConnectionError as e:
        return {
            'status_code': None,
            'response_time': None,
            'is_up': False,
            'error_message': f'Connection Error: {str(e)}'
        }
    
    except Exception as e:
        return {
            'status_code': None,
            'response_time': None,
            'is_up': False,
            'error_message': str(e)
        }

def determine_incident_type(result, threshold): #result is output of checkurl-monitor_webs


    if result['error_message']:
        if 'timeout' in result['error_message'].lower():
            return 'timeout'
        elif 'ssl' in result['error_message'].lower():
            return 'ssl_error'
        else:
            return 'connection_error'
    
    if result['status_code']:
        if result['status_code'] >= 500:
            return 'server_error'
        elif result['status_code'] >= 400:
            return 'client_error'
    
    if result['response_time'] and result['response_time'] > threshold:
        return 'slow_response'
    
    return None

def monitor_website(app, website_id):
    with app.app_context():
        website = Website.query.get(website_id)
        if not website or not website.is_active:
            return
        
        urls_to_check = [(website.url, website.name)]
        for subpage in website.subpages.filter_by(is_active=True).all():
            urls_to_check.append((subpage.url, subpage.name or subpage.url))
        
        for url, name in urls_to_check:
            result = check_url(url)
            
            check = MonitoringCheck(
                website_id=website.id,
                status_code=result['status_code'],
                response_time=result['response_time'],
                is_up=result['is_up'],
                error_message=result['error_message']
            )
            db.session.add(check)
            
            incident_type = determine_incident_type(result, website.response_threshold)
            
            if incident_type:
                active_incident = Incident.query.filter_by(
                    website_id=website.id,
                    incident_type=incident_type,
                    is_resolved=False
                ).first()
                
                if not active_incident:
                    incident_info = INCIDENT_TYPES.get(incident_type, {})
                    severity = 'critical' if incident_type in ['timeout', 'server_error', 'connection_error'] else 'warning'
                    
                    incident = Incident(
                        website_id=website.id,
                        incident_type=incident_type,
                        severity=severity,
                        description=f"{name}: {result['error_message'] or 'Status ' + str(result['status_code'])}",
                        probable_cause=incident_info.get('cause', 'Unknown'),
                        suggestion=incident_info.get('suggestion', 'Investigate the issue'),
                        started_at=datetime.utcnow()
                    )
                    db.session.add(incident)
                    logger.warning(f"New incident detected for {name}: {incident_type}")
            else:
                active_incidents = Incident.query.filter_by(
                    website_id=website.id,
                    is_resolved=False
                ).all()
                
                for incident in active_incidents:
                    incident.is_resolved = True
                    incident.ended_at = datetime.utcnow()
                    incident.duration_seconds = int((incident.ended_at - incident.started_at).total_seconds())
                    logger.info(f"Incident resolved for {name}: {incident.incident_type}")
        
        db.session.commit()
        logger.info(f"Monitoring check completed for {website.name}")

def get_website_stats(website_id, period='day'):
    now = datetime.utcnow()
    
    if period == 'day':
        start_time = now - timedelta(days=1)
    elif period == 'week':
        start_time = now - timedelta(weeks=1)
    elif period == 'month':
        start_time = now - timedelta(days=30)
    elif period == 'year':
        start_time = now - timedelta(days=365)
    else:
        start_time = now - timedelta(days=1)
    
    checks = MonitoringCheck.query.filter(
        MonitoringCheck.website_id == website_id,
        MonitoringCheck.checked_at >= start_time
    ).all()
    
    incidents = Incident.query.filter(
        Incident.website_id == website_id,
        Incident.started_at >= start_time
    ).all()
    
    total_checks = len(checks)
    up_checks = sum(1 for c in checks if c.is_up)
    uptime_percentage = (up_checks / total_checks * 100) if total_checks > 0 else 100
    
    response_times = [c.response_time for c in checks if c.response_time]
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    total_downtime = sum(i.duration_seconds or 0 for i in incidents if i.is_resolved)
    
    return {
        'uptime_percentage': round(uptime_percentage, 2),
        'avg_response_time': round(avg_response_time, 2),
        'total_checks': total_checks,
        'total_incidents': len(incidents),
        'total_downtime_seconds': total_downtime,
        'active_incidents': sum(1 for i in incidents if not i.is_resolved)
    }
