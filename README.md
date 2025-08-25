# MrSender

MrSender is a system for sending email to leads and call them soon after

## How does it work

MrSender takes information about a lead and generates a message according to a prompt and the information you have about the lead. At the same time it creates a new contact on a MrCall phone assistant.

It then sends the message through sendgrid APIs. When the lead opens the email, MrSender makes a call to MrCall's APIs and generates an outbound call to the lead.

## Configuration

The configuration file needs:

- OPENAI_KEY for generating the message
- SENDGRID_KEY for sending email messages
- MRCALL_USER, MRCALL_PASSWORD and MRCALL_BUSINESS_ID for making the calls
- EMAIL_PROMPT is the prompt used for generating the messages
- DATABASE_URL pointing to the SQLite database (default is `sqlite:///./mailsender.db`)

## Data about the leads

The data about the lead are stored in a SQLite table named `lead`. Mandatory fields are:

- `phone_number`
- `email_address`
- `opt_in` (true/false)
- `other_info` (JSON)

Install dependencies and create the database tables with:

```
pip install -r requirements.txt
python scripts/create_lead_table.py
```

## Workflow details

MrSender offers a webservice (FastAPI)

1. For each lead with opt_in == true, MrSender generates a personalized email using the prompt stored in EMAIL_PROMPT.
2. Send an email to each lead through sendgrid.
3. When a lead opens the email, MrSender triggers a call to mrcall.ai API for calling the lead.
