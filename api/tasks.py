from time import sleep
from celery import shared_task


@shared_task
def sending_emails(message):
    print("sending 10k messages...")
    print(message)
    sleep(10)
    print("emails sent successfully!")
