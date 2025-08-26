# MrSender

MrSender is a system for sending email to leads and call them soon after

## How does it work

MrSender takes information about a lead and generates a message according to a prompt and the information you have about the lead. At the same time it creates a new contact on a MrCall phone assistant.

It then sends the message through sendgrid APIs. SendGrid posts events such as email opens to the `/tracking` webhook, which records them in the `campaign` table and can be used to trigger calls to MrCall.

## Configuration

Configuration values are read from a `settings.ini` file located at the
project root (a symlink to `app/resources/settings_template.ini`). Populate the
`[settings]` section with the following keys:

- `openai_key` for generating the message
- `sendgrid_key` for sending email messages
- `mrcall_user`, `mrcall_password` and `mrcall_business_id` for making the calls
- `email_prompt` is the prompt used for generating the messages
- `database_url` pointing to the SQLite database (default is `sqlite:///./mailsender.db`)

## Installation

Create and activate a virtual environment, then install the dependencies:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r app/requirements.txt
```

You can also run the application with Docker:

```
docker-compose up --build
```

## Usage

### Prepare the database

```
python app/scripts/create_lead_table.py
python app/scripts/create_campaign_table.py
python app/scripts/reset_leads.py
```

### Run the API

```
uvicorn app.main:app --reload
```

### Send campaign emails

```
python app/scripts/send_campaign_emails.py --sender you@example.com
```

## Data about the leads

The data about the lead are stored in a SQLite table named `lead`. Mandatory fields are:

- `phone_number`
- `email_address`
- `opt_in` (true/false)
- `custom_args` (JSON)
 
## Campaign tracking

SendGrid sends POST requests to `/tracking` with payloads like:

```
{
  "email": "user@example.com",
  "timestamp": 1692981125,
  "event": "open",
  "sg_message_id": "xxx.yyy.zzz",
  "smtp-id": "<20250825121500.12345@domain.com>",
  "custom_args": {
    "user_id": "42",
    "order_id": "9876"
  }
}
```

These events are stored in the `campaign` table.

## Workflow details

MrSender offers a webservice (FastAPI)

1. For each lead with opt_in == true, MrSender generates a personalized email using the prompt stored in EMAIL_PROMPT.
2. Send an email to each lead through sendgrid.
3. SendGrid posts email events to `/tracking`, storing them for further processing.

## Testing

Run a syntax check across all Python modules:

```
python -m py_compile $(git ls-files '*.py')
```
