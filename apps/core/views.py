from django.core.management import call_command
from django.http import HttpResponse
# Temporary view for flushing database

def flush_database(request):
    call_command('flush', interactive=False)
    return HttpResponse("Database flushed successfully")

# YOU SHOULD 100% REMOVE THIS VIEW BEFORE DEPLOYMENT