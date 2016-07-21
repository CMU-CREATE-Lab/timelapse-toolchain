# -*- coding: utf-8 -*-
import os

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings

from .forms import CSVForm
from .csv_to_zip import main as build_zip

OUT_DIR = os.path.join(getattr(settings, "BASE_DIR"), 'uploads')

def upload_csv(request):
    if request.method == 'POST':
        form = CSVForm(request.POST, request.FILES)
        if form.is_valid():
            # Create an object to persist the metadata about the csv (e.g. id
            # in db or sha1 of the contents)
            csv_file = request.FILES['csvfile']
            save_csv(csv_file)
            # Generate binary
            output_path = os.path.join(OUT_DIR, csv_file.name)
            build_zip(output_path)
            # Redirect to result page, would pass some way to identify input
            # data. For now, simply use filename.
            return HttpResponseRedirect(reverse('result'))
    else:
        form = CSVForm()

    return render(
        request,
        'upload.html',
        {'form': form},
    )


def save_csv(csv_file):
    output_path = os.path.join(OUT_DIR, csv_file.name)
    with open(output_path, 'wb') as output_file:
        if csv_file.multiple_chunks:
            for c in csv_file.chunks():
                output_file.write(c)
        else:
            output_file.write(csv_file.read())


def result(request):
    return render(request, 'result.html')
