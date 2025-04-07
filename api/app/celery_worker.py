from app.tasks import celery_app

if __name__ == '__main__':
    args = ['worker', '--loglevel=INFO']
    celery_app.worker_main(argv=args)