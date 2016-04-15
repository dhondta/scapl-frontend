from collections import OrderedDict
from .models import DataItem, DataList, DataSequence, ItemListAssociations, ListSequenceAssociations


def get_scheme(sequence_id=1):
    """
    This function retrieves a data sequence based on its ID.

    The resulting structure is a dictionary formatted like follows:

    {
        DS_object: OrderedDict(
            DL006_object: [
                DI00005_object,
                DI00002_object,
                ...
            ],
            DL017_object: [
                DI00011_object,
                ...
            ],
            ...
        )
    }

    """
    scheme = {}
    ds = DataSequence.objects.get(id=sequence_id)
    scheme[ds] = OrderedDict()
    for dl_association in ListSequenceAssociations.objects.filter(sequence=ds.id):
        dl = DataList.objects.get(id=dl_association.list_id)
        scheme[ds][dl] = []
        for di_association in ItemListAssociations.objects.filter(list=dl.id):
            scheme[ds][dl].append(DataItem.objects.get(id=di_association.item_id))
    return scheme
