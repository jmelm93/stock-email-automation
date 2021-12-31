
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from pretty_html_table import build_table

from dotenv import load_dotenv
load_dotenv()

import os

def send_email(subject_line, content, dataframe=None, all_stock_data = None):
    
    
    # https://pypi.org/project/pretty-html-table/
    pretty_table = build_table(dataframe, 'blue_light', font_size='15px', width='500px', text_align='center' )
    api_key = os.environ.get('SENDGRID_API')
    email_from = os.environ.get('SENDGRID_FROM')
    email_to = os.environ.get('SENDGRID_TO')

    if len(dataframe) is not None:
        message = Mail(
        from_email=email_from,
        to_emails=email_to,
        subject=subject_line,
        html_content=f'{content} <br><br> {pretty_table}' )
        
        try:
            sg = SendGridAPIClient(api_key)
            response = sg.send(message)
            print(response.status_code, response.body, response.headers)
        except Exception as e:
            print(e.message)

    if len(dataframe) is None:
        message = Mail(
        from_email=email_from,
        to_emails=email_to,
        subject=subject_line,
        html_content=f'{content}' )
        try:
            sg = SendGridAPIClient(api_key)
            response = sg.send(message)
            print(response.status_code, response.body, response.headers)
        except Exception as e:
            print(e.message)

