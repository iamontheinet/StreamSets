import time

for record in records:
   try:
     for change in record.value['change']:
       newRecord = sdcFunctions.createRecord(record.sourceId + str(time.time()))
       newRecord.value = {}

       newRecord.attributes['xid'] = str(record.value['xid'])

       newRecord.attributes['nextlsn'] = record.value['nextlsn']
       newRecord.attributes['timestamp'] = record.value['timestamp']
       newRecord.attributes['kind'] = change['kind']
       newRecord.attributes['schema'] = change['schema'] 
       newRecord.attributes['jdbc.tables'] = change['table']

       if change['kind'] == 'insert':
          newRecord.attributes['sdc.operation.type'] = '1'
       if change['kind'] == 'delete':
          newRecord.attributes['sdc.operation.type'] = '2'
       if change['kind'] == 'update':
          newRecord.attributes['sdc.operation.type'] = '3'

       if 'columnnames' in change:
          columns = change['columnnames']
          types = change['columntypes']
          values = change['columnvalues']
       else:
          columns = change['oldkeys']['keynames']
          types = change['oldkeys']['keytypes']
          values = change['oldkeys']['keyvalues']

       for j in range(len(columns)):
          name = columns[j]
          type = types[j]
          value = values[j]
          # add data type conversions here. 
          if 'numeric' in type or 'float' in type or 'double precision' in type:
             newRecord.value[name] = float(value) # python float == java double 
          else: 
             newRecord.value[name] = value

       output.write(newRecord)

   except Exception as e:
     # Send record to error
     error.write(record, str(e))
