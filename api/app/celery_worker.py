from app.tasks import celery_app

if __name__ == '__main__':
    args = ['--loglevel=INFO','--concurrency=5']
    celery_app.worker_main(argv=args)