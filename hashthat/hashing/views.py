from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect
import hashlib

from .forms import HashForm
from .models import Hash

# Create your views here.
def home(request):
    if request.method == 'POST':
        filled_form = HashForm(request.POST)
        if filled_form.is_valid():
            text = filled_form.cleaned_data['text']
            texthash = hashlib.sha256(text.encode('utf-8')).hexdigest()
            try:
                Hash.objects.get(hash=texthash)
            except Hash.DoesNotExist:
                hashobj = Hash()
                hashobj.text = text
                hashobj.hash = texthash
                hashobj.save()
            return redirect('hash', hashstr=texthash)
                
    form = HashForm()
    return render(request, 'hashing/home.html', 
                {'form': form})


def hash_(request, hashstr):
    try:
        hashobj = Hash.objects.get(hash=hashstr)
    except Hash.DoesNotExist:
        raise Http404(f'Unknown hash {hashstr}')
    return render(request, 'hashing/hash.html', {'hashobj': hashobj})


def quickhash(request):
    text = request.GET['text']
    return JsonResponse(
        {'hash': hashlib.sha256(text.encode('utf-8')).hexdigest()}
    )
