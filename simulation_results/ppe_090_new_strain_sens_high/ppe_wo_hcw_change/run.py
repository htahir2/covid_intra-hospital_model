"""

    @author: hannantahir

"""

from intra_hospital.model import *
from intra_hospital import params
import time

start = time.time()
covid19_model = IntraHospModel()
for i in range(params.max_iter):
    covid19_model.step()

end = time.time()
elapsed = end - start
print('Total simulation time is = ', elapsed/60, ' Minutes')