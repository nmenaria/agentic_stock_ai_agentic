from apscheduler.schedulers.background import BackgroundScheduler
from agent import run_agentic_scan

DEFAULT_COMPANIES = ['Apple', 'Microsoft', 'Tesla', 'Alphabet', 'Amazon']

scheduler = BackgroundScheduler()
scheduler.add_job(lambda: run_agentic_scan(DEFAULT_COMPANIES, send_email_flag=True),
                  'interval', minutes=60)
scheduler.start()
