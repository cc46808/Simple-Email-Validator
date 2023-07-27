import re
import dns.resolver
import smtplib
import pandas as pd
from datetime import datetime
from tqdm import tqdm
from email.utils import parseaddr
import time
import sys

# Regular expression for validating an Email
email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

def validate_email_syntax(email):
    if re.match(email_regex, email):
        return "Valid"
    else:
        return "Invalid"

def validate_email_domain(email):
    domain = email.split('@')[1]
    try:
        if dns.resolver.resolve(domain, 'MX'):
            return "Valid"
    except dns.resolver.NoAnswer:
        return "Invalid"
    except dns.resolver.NXDOMAIN:
        return "Invalid"

def validate_email_smtp(email):
    _, domain = parseaddr(email)[1].rsplit('@', 1)
    mx_records = dns.resolver.resolve(domain, 'MX')
    mx_record = str(mx_records[0].exchange)
    server = smtplib.SMTP()
    server.set_debuglevel(0)
    server_down = "Up"
    catch_all = "No"
    try:
        server.connect(mx_record)
        server.helo(server.local_hostname)
        server.mail('')
        code, _ = server.rcpt(email)
        # Check for catch-all
        catch_all_code, _ = server.rcpt('non_existent_user@' + domain)
        if catch_all_code == 250:
            catch_all = "Yes"
    except smtplib.SMTPConnectError:
        server_down = "Down"
        return "Unknown", server_down, catch_all
    except smtplib.SMTPServerDisconnected:
        return "Unknown", server_down, catch_all
    finally:
        try:
            server.quit()
        except smtplib.SMTPServerDisconnected:
            pass

    if code == 250:
        return "Valid", server_down, catch_all
    else:
        return "Invalid", server_down, catch_all
    
def calculate_score(syntax_status, domain_status, smtp_status, server_status, catch_all_status):
    num_checks = 5
    increment = 1 / num_checks
    score = 0
    if domain_status != "Valid" or smtp_status == "Invalid":
        return 0.0
    if syntax_status == "Valid": score += increment
    if domain_status == "Valid": score += increment
    if smtp_status == "Valid": score += increment
    elif smtp_status == "Unknown": score += 0.1
    if server_status == "Up": score += increment
    if catch_all_status == "No": score += increment
    return round(score, 3)

def validate_email_in_csv(file_path):
    df = pd.read_csv(file_path)

    results = []

    for column in df.columns:
        if df[column].astype(str).str.contains(email_regex).any():
            for email in tqdm(df[column]):
                start_time = time.time()
                syntax_status = validate_email_syntax(str(email))
                domain_status = validate_email_domain(str(email)) if syntax_status == "Valid" else "Invalid"
                smtp_status, server_status, catch_all_status = validate_email_smtp(str(email)) if domain_status == "Valid" else ("Invalid", "N/A", "N/A")
                end_time = time.time()
                score = calculate_score(syntax_status, domain_status, smtp_status, server_status, catch_all_status)
                validation_time = round(end_time - start_time, 2)  # Time in seconds, rounded to two decimal places

                # Determine confidence level
                if score < 0.2:
                    confidence = 'Low'
                elif 0.2 <= score < 0.4:
                    confidence = 'Slight'
                elif 0.4 <= score < 0.6:
                    confidence = 'Moderate'
                elif 0.6 <= score < 0.8:
                    confidence = 'High'
                elif 0.8 <= score < 1:
                    confidence = 'Excellent'
                else:
                    confidence = 'Perfect'

                results.append((email, syntax_status, domain_status, smtp_status, server_status, catch_all_status, score, validation_time, confidence))

                # Add a delay between each SMTP verification
                time.sleep(0.001)

    return results

def write_results_to_csv(results, file_path):
    results_df = pd.DataFrame(results, columns=['Email', 'Syntax', 'Domain', 'SMTP', 'SMTP Server Status', 'Catch-All', 'Score', 'Validation Time (s)', 'Confidence'])

    now = datetime.now()
    date_time = now.strftime("%m%d%y%H%M%S")

    new_file_path = file_path.rsplit('.', 1)[0] + "_results_" + date_time + ".csv"

    results_df.to_csv(new_file_path, index=False)
    print(f"Results written to {new_file_path}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python simple.py /path/to/file.csv")
        return
    file_path = sys.argv[1]
    results = validate_email_in_csv(file_path)
    write_results_to_csv(results, file_path)

if __name__ == "__main__":
    main()
