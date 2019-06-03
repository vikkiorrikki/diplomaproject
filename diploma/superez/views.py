from django.shortcuts import render
from django.conf import settings
import os
import sys
sys.path.insert(0, 'D:\\wamp64\\www\\diploma\\superez')
sys.path.insert(0, 'D:\\wamp64\\www\\diploma\\superez\\srezmodel')
from superez.srezmodel.inference import inference


def index(request):
    return render(request, "index.html")


from django.shortcuts import render

from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.urls import reverse

from superez.models import Document
from superez.forms import DocumentForm

def handle_uploaded_file(f, path_to_save):
    with open(path_to_save, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

files_path = "superez/images"

def list(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():

            print("="*30, request.FILES["docfile"])

            handle_uploaded_file(request.FILES["docfile"], os.path.join(files_path, str(request.FILES["docfile"])))

            # newdoc = Document(docfile = request.FILES['docfile'])
            # newdoc.save()

            inference(os.path.join(files_path, str(request.FILES["docfile"])))

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('list'))
    else:
        form = DocumentForm() # A empty, unbound form

    # Load documents for the list page
    # documents = Document.objects.all()
    documents = [file for file in os.listdir(files_path) if os.path.isfile(os.path.join(files_path, file))]
    print("!"*30, documents)


    # Render list page with the documents and the form
    return render(request, 'list.html', {'documents': documents, 'form': form})