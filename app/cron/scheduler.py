from apscheduler.schedulers.background import BackgroundScheduler
import os
from datetime import datetime
from app.utils.update_daily_calories import migrate_daily_to_overall


_scheduler = None 

def update_overall_calories():
    migrate_daily_to_overall()
    return True

def init_scheduler(app):
    """Initialize the scheduler with the Flask app context."""
    global _scheduler
        
        
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        return
    
    if _scheduler is not None:
        return
    
    _scheduler = BackgroundScheduler()
    
    _scheduler.add_job(
        func=update_overall_calories,
        trigger='interval',
        minutes=5,
        id='update_calories',
        max_instances=1,
        coalesce=True,
        next_run_time=datetime.now()
    )
    
    _scheduler.start()
    
    import atexit
    atexit.register(lambda: _scheduler.shutdown(wait=False))