import pandas as pd
import os
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys
import time

load_dotenv()

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = 'anyushah@gmail.com'
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

EVENT_NAME = "Subscription-Free Futures"
EVENT_DATE = "This Thursday"
EVENT_TIME = "6:30 PM - 9:00 PM"
EVENT_VENUE = "CIC"
RSVP_LINK = "https://lu.ma/subscriptions"
UNSUBSCRIBE_LINK = "https://intellectual-start-127187.framer.app"  


if SMTP_PASSWORD is None:
    print("Error: SMTP_PASSWORD not found in environment variables")
    sys.exit(1)

def send_email(to_address, subject, message, retry_count=3, delay=5):
    """Send email with retry mechanism"""

    if not to_address or '@' not in to_address:
        print(f"Invalid email address: {to_address}")
        return False
        

    msg = MIMEMultipart()
    msg['From'] = SMTP_USERNAME
    msg['To'] = to_address
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'html'))
    
    # Retry loop
    for attempt in range(retry_count):
        try:
            print(f"Connecting to SMTP server {SMTP_SERVER}:{SMTP_PORT}...")
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.set_debuglevel(1)  
            print("Starting TLS...")
            server.starttls()
            
            print("Attempting login...")
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            
            print(f"Sending message to {to_address}...")
            server.send_message(msg)
            server.quit()
            
            print(f"Email sent successfully to {to_address}")
            return True
            
        except Exception as e:
            print(f"Attempt {attempt+1}/{retry_count} failed to send email to {to_address}")
            print(f"Error details: {str(e)}")
            
            if attempt < retry_count - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("All retry attempts failed")
                return False

def main():
    successful = 0
    failed = 0
    
    try:
        # Read Excel file
        df = pd.read_csv('contacts.csv')
        
        # Validate Excel has required columns
        if 'Email' not in df.columns:
            print("Error: Excel file must contain an 'Email' column")
            sys.exit(1)
            
        for index, row in df.iterrows():
            # Get name from Excel, use 'there' as fallback if name is missing or empty
            name = row.get('Name', 'there')  # Will return 'there' if Name column is empty
            email = row.get('Email')  # No default needed for email since we check it later
            
            if pd.isna(email):
                print(f"Skipping row {index + 2} with missing email")
                failed += 1
                continue
            
            # HTML Email template
            message = f"""<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.5;
            color: #333333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            margin-bottom: 20px;
        }}
        .event-details {{
            background-color: #f7f7f7;
            padding: 15px;
            border-left: 4px solid #0066cc;
            margin: 15px 0;
        }}
        .cta-button {{
            background-color: #0066cc;
            color: white !important;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 4px;
            display: inline-block;
            margin: 15px 0;
        }}
        .cta-button:link, 
        .cta-button:visited, 
        .cta-button:hover, 
        .cta-button:active {{
            color: white !important;
            text-decoration: none;
        }}
        .footer {{
            margin-top: 30px;
            font-size: 14px;
            color: #666666;
            border-top: 1px solid #eeeeee;
            padding-top: 15px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <p>Hi {name},</p>
            <p>I hope you're having a great start to your week. Based on your interest in previous GenAI events, I wanted to personally invite you to our upcoming event:</p>
        </div>
        
        <div class="event-details">
            <h2><b>{EVENT_NAME}</b></h2>
            <p>A deep dive into disruptive monetization strategies without recurring fees</p>
            <p><strong>When:</strong> {EVENT_DATE} | {EVENT_TIME}</p>
            <p><strong>Where:</strong> {EVENT_VENUE} | Mosaic Room (3rd Floor)</p>
        </div>
        
        <p>If you're tired of managing endless SaaS subscriptions and monthly invoices, this event is for you. Join us to explore alternative revenue models with the founder of Ares and co-founder of Sundai Club.</p>
        
        <a href="{RSVP_LINK}" class="cta-button">RSVP Here (Limited Seats)</a>
        
        <p>Looking forward to seeing you there!</p>
        
        <div class="footer">
            <p>Unsubscribing,<br>
            Ananya Shah<br>
            Boston Co-Lead @ GenAI Collective</p>
            <p><small>If you'd prefer not to receive future event invitations, simply <a href="{UNSUBSCRIBE_LINK}">click here</a>.</small></p>
        </div>
    </div>
</body>
</html>"""

            subject = f"Invitation: Flash Event from GenAI - {EVENT_NAME}"
            
            # Add rate limiting to avoid SMTP server throttling
            if successful > 0:
                time.sleep(1)  # Wait 1 second between emails
            
            if send_email(email, subject, message):
                successful += 1
            else:
                failed += 1
                
    except FileNotFoundError:
        print("Error: contacts.xlsx file not found")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)
        
    print(f"\nSummary: {successful} emails sent successfully, {failed} failed")

if __name__ == "__main__":
    main()