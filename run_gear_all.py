#!/usr/bin/env python
import sys
sys.exit()
import flywheel
fw = flywheel.Client()
res = fw.search({'structured_query':
                 'group.label = "MRRC" AND project.label LIKE "wpc-8620" AND acquisition.label LIKE "*"',
                 'return_type': 'acquisition'},size=500)
acq = [fw.get(x.acquisition.id) for x in res]
acq_need = [x for x in acq if len(x.files) >= 1 and x.files[0].get('classification') == {}]

gear = fw.lookup("gears/dicom-mr-classifier")
example_scitran = fw.get_job("67081273068b3d34caefceba")

# NB. test with acq_need[0:1], then run acq_need[1:]
jobids = [gear.run(tags=['script','scitran'], config={},
                   inputs={'dicom': x.files[0]}, destination=x) for x in acq_need[1:]]

# 20241010 -- gear rule picked up after this. don't need to rerun dcm2niix
# example_dcm2nii = fw.get_job("6705d9d4b38c56e401b1c25a")
# # example_dcm2nii.config.inputs.keys() 'dcm2niix_input'
# # print(fw.get_gear(example_dcm2nii.gear_id).gear.name)
#
# gear = fw.lookup("gears/dcm2niix")
# jobids = [gear.run(tags=['script','dcm2niix'], config={},
#                    inputs={'dcm2niix_input': x.files[0]}, destination=x) for x in acq_need[0:1]]
