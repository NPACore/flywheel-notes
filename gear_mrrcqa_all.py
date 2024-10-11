res = fw.search({'structured_query':
                 'group.label = "MRRC" AND project.label LIKE "Prisma*QA" AND acquisition.label LIKE "*ep2d*"',
                 'return_type': 'acquisition'},size=500)
acq = [fw.get(x.acquisition.id) for x in res]
acq_need = [x for x in acq if len(x.files) == 1]

gear = fw.lookup("gears/mrrcqa")

jobids = [gear.run(tags=['hpc','mrrcqa'], config={}, inputs={'phantom_dicom': x.files[0]}, destination=x) for x in acq_need[1:]]
