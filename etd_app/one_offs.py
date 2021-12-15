'''One-off scripts that need to be run'''
import requests
from . import models


def populate_department_bdr_collection_pids():
    departments = models.Department.objects.all()
    for index, dept in enumerate(departments):
        print(f'{index} {dept.name}')
        if not dept.bdr_collection_pid:
            if dept.bdr_collection_id:
                url = f'https://repository.library.brown.edu/api/collections/{dept.bdr_collection_id}/'
                r = requests.get(url)
                if r.ok:
                    collection_info = r.json()
                    pid = collection_info.get('pid')
                    if pid:
                        dept.bdr_collection_pid = pid
                        dept.save()
                    else:
                        print(f'ERROR: no pid for collection {dept.bdr_collection_id}')
                else:
                    print(f'API ERROR: {r.status_code} {r.text}')
            else:
                print(f'ERROR: no bdr_collection_id for {dept}')
