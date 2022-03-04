from django.forms import ValidationError
from django.http import JsonResponse
from lists.forms import ExistingListItemForm

from lists.forms import EMPTY_ITEM_ERROR
from lists.forms import DUPLICATE_ITEM_ERROR
from lists.models import List

def list(request, list_id):
    list_ = List.objects.get(id=list_id)

    if request.method == 'POST':
        form = ExistingListItemForm(for_list=list_, data=request.POST)
        if form.is_valid():
            form.save()
        else:
            return JsonResponse({'error': form.errors['text'][0]}, status=400)

    data = [
        {'id': item.id, 'text': item.text}
        for item in list_.item_set.all()
    ]

    return JsonResponse(data=data, safe=False)
