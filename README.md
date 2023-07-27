# Simple-Email-Validator

# Introduction

No API's, no limits. 

This Python script checks the validity of email addresses in a CSV file. The validation process includes syntax checking, domain validation, SMTP validation, SMTP server status checking, and catch-all checking. 

The results, including a score and confidence level for each email address, are written to a new CSV file.

## Prerequisites

This script requires Python 3.7 or higher, and the following Python libraries:
- re
- dns.resolver
- smtplib
- pandas
- tqdm
- email.utils
- time
- sys

## Usage

Run the script from the command line, passing the path to the CSV file as a parameter:

```bash
python simple.py /path/to/file.csv
```

The script will validate the email addresses in the file and write the results to a new CSV file in the same location as the input file. The new file will have the same name as the input file, but with "_results_" and a timestamp appended to the name.

## Output

The output CSV file includes the following columns:
- Email: The email address
- Syntax: Whether the syntax of the email address is valid
- Domain: Whether the domain of the email address is valid
- SMTP: Whether the SMTP check passed
- SMTP Server Status: Whether the SMTP server is up
- Catch-All: Whether the email address is set to catch-all
- Score: A score between 0 and 1 indicating the likelihood that the email address is valid
- Validation Time (s): The time taken to validate the email address
- Confidence: A confidence level (Low, Slight, Moderate, High, Excellent, Perfect) based on the score

## Note

This script includes a small delay between SMTP verifications to avoid being blocked by the SMTP server. 
