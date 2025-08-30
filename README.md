# MrSender

MrSender is a system for sending email to contacts and call them soon after

## How does it work

MrSender takes information about a contact and generates a message according to a prompt and the information you have about the contact. The assistant is instructed to craft simple, human-like email bodies for the contact. At the same time it creates a new contact on a MrCall phone assistant.

It then sends the message through sendgrid APIs. SendGrid posts events such as email opens to the `/tracking` webhook, which records them in the `campaign` table and can be used to trigger calls to MrCall.

## Configuration

Configuration values are read from `app/resources/settings.ini`. Populate the
`[settings]` section with the following keys:

- `openai_key` for generating the message
- `sendgrid_key` for sending email messages
- `from_name` displayed as the sender name in outgoing emails
- `mrcall_username`, `mrcall_password` and `mrcall_business_id` for making the calls
- `email_prompt` instructs the assistant to generate a simple, human-style email body for the contact
- `database_url` pointing to the SQLite database (default is `sqlite:///./mailsender.db`)
- `body` optional HTML template used when `--body-ai 0`; placeholders like `{name}` are
  replaced with values from `contact.custom_args`

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
python app/scripts/create_contact_table.py
python app/scripts/create_campaign_table.py
python app/scripts/reset_contacts.py
```

### Run the API

Start the API server from the repository root:

```
python app/main.py --debug
```

Use `--debug` for verbose output or set the `LOG_LEVEL` environment
variable to another level:

```
LOG_LEVEL=warning python app/main.py
```

Alternatively, run `uvicorn` directly and control verbosity with its
`--log-level` flag:

```
uvicorn app.main:app --reload --log-level debug
```

Use `--debug` for verbose output or set the `LOG_LEVEL` environment
variable to another level:

```
cd app && uvicorn main:app --reload --log-level debug
# or
PYTHONPATH=app uvicorn main:app --reload --log-level debug
```

### Send campaign emails

```
python app/scripts/send_campaign_emails.py --id campaign_id --sender you@example.com [--body-ai 0|1]
```

Use `--body-ai 0` to send the `body` template from the configuration instead of
generating content with OpenAI. Unmatched placeholders in the template are
removed.

## Data about the contacts

The data about the contact are stored in a SQLite table named `contact`. Mandatory fields are:

- `business_id`
- `first`
- `last`
- `organizations` (JSON)
- `emails` (JSON)
- `variables` (JSON containing keys like `address`, `phone_number`, `opt_in`, `phonecall_made`, `phonecall_answered`, `sms_sent`, `wa_sent`)
- `custom_args` (JSON)
 
## Campaign tracking

SendGrid sends POST requests to `/tracking` with payloads like:

```
[
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
]
```

Each object in the array is stored in the `campaign` table.

## Workflow details

MrSender offers a webservice (FastAPI)

1. For each contact with opt_in == "true", MrSender generates a personalized email using the prompt stored in EMAIL_PROMPT.
2. Send an email to each contact through sendgrid.
3. SendGrid posts email events to `/tracking`, storing them for further processing.

## Testing

Run a syntax check across all Python modules:

```
python -m py_compile $(git ls-files '*.py')
```
