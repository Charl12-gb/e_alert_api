import string
import random
import uuid
from ..models import Documents

def generateNumero(prefix='EXER-E'):
    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return prefix + random_string

def generateUniqueUuid():
    while True:
        unique_uuid = uuid.uuid4()
        # Vérifier si l'UUID n'est pas déjà utilisé pour le même group_number
        if not Documents.objects.filter(group_number=unique_uuid).exists():
            return unique_uuid