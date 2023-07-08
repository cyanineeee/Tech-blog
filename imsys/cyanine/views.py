from django.shortcuts import render

def main(request):
    return render(request,'./cyanine/main.html')