from celery import shared_task


@shared_task
def smoke(x):
    return x
