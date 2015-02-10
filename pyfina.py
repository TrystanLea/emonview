"""

  This code is released under the GNU Affero General Public License.
  
  OpenEnergyMonitor project:
  http://openenergymonitor.org

"""

import struct, math, os

class pyfina(object):


    padding_mode = "null"

    # Data directory of pyfina files
    datadir = ""
    
    # Cache meta data in memory
    metadata_cache = {}
    
    # Buffer timeseries data
    buffers = {}
    
    # Last value tmp store
    lastvalue_cache = {}
    
    def __init__(self,datadir):
        self.buffers = {}
        self.datadir = datadir
    
    
    def create(self,filename,interval):
        if interval<5:
            interval = 5;
        
        meta = self.get_meta(filename)
        
        # Check to ensure we dont overwrite an existing feed
        if not meta:
            # Set initial feed meta data
            meta = {'npoints':0, 'interval':interval, 'start_time':0}
            
            self.create_meta(filename,meta)
            
            # In php version: CREATE BLANK DATA FILE
            fh = open(self.datadir+filename+".dat","wb")
            fh.close()
            
        # In php version: VERIFY META FILE EXISTS


    # Prepare inserts datapoint into in-memory data buffer
    # Data is then saved to disk using the save method 
    def prepare(self,filename,timestamp,value):
        # In php version: parse input values
        # In php version: check that timestamp is within range
        timestamp = round(timestamp)
        
        # If meta data file does not exist then exit
        meta = self.get_meta(filename)
        if not meta:
            return False
            # or: 
            # meta = {
            #     'interval': interval,
            #     'start_time': math.floor(timestamp / interval) * interval
            # }
            # self.create_meta(filename,meta)
            
        meta['npoints'] = self.get_npoints(filename)
        
        #Calculate interval that this datapoint belongs too
        timestamp = math.floor(timestamp / meta['interval']) * meta['interval']
        
        # If this is a new feed (npoints == 0) then set the start time to the current datapoint
        if (meta['npoints'] == 0 and meta['start_time']==0):
            meta['start_time'] = timestamp
            self.create_meta(filename,meta)

        if (timestamp < meta['start_time']):
            # LOG: timestamp older than feed start time
            return False # in the past
        
        pos = int(math.floor((timestamp - meta['start_time']) / meta['interval']))
        last_pos = meta['npoints'] - 1;

        # Implementation does not currently allow for updating existing values
        # Ensure that new value is a new value
        if pos>last_pos:
            npadding = (pos - last_pos)-1
            
            if not filename in self.buffers:
                self.buffers[filename] = ""

            if npadding>0:
                padding_value = 'nan'
                
                if self.padding_mode=="join":
                    last_val = self.lastvalue(filename)
                    div = (value - last_val) / (npadding+1)
                    padding_value = last_val
                     
                for n in range(npadding):
                    if self.padding_mode=="join": padding_value += div
                    self.buffers[filename] += struct.pack("f",float(padding_value))
            
            self.buffers[filename] += struct.pack("f",float(value))
            self.lastvalue_cache[filename] = value

        return value
    
    # Save data in data buffers to disk
    # Writing data in larger blocks saves reduces disk write load as 
    # filesystems have a minimum IO size which are usually 512 bytes or more.
    def save(self):
        byteswritten = 0
        for name, data in self.buffers.iteritems():
            fh = open(self.datadir+name+".dat","ab")
            fh.write(data)
            fh.close()
            
            byteswritten += len(data)

        # Reset buffers
        self.buffers = {}
        
        return byteswritten
            
            
    def data(self,filename,start,end,outinterval):

        start = float(start) / 1000.0
        end = float(end) / 1000.0
        outinterval = int(outinterval)
        
        meta = self.get_meta(filename)
        if not meta:
            return False
        meta['npoints'] = self.get_npoints(filename)    
            
            
        if outinterval<meta['interval']:
            outinterval = meta['interval']
            
        dp = int(math.ceil((end-start)/outinterval))
        end = start + (dp*outinterval)
        
        if dp<1: 
            return False
        
        # The number of datapoints in the query range:
        dp_in_range = (end - start) / meta['interval']
        
        # Divided by the number we need gives the number of datapoints to skip
        # i.e if we want 1000 datapoints out of 100,000 then we need to get one
        # datapoints every 100 datapoints.
        skipsize = round(dp_in_range / dp)
        if skipsize<1:
            skipsize = 1
        
        # Calculate the starting datapoint position in the timestore file
        if start>meta['start_time']:
            startpos = math.ceil((start - meta['start_time']) / meta['interval'])
        else:
            start = math.ceil(meta['start_time'] / outinterval) * outinterval
            startpos = math.ceil((start - meta['start_time']) / meta['interval'])
         
        data = []
        timestamp = 0
        i = 0
        
        fh = open(self.datadir+filename+".dat","rb")
        while timestamp<=end:
            # position steps forward by skipsize every loop
            pos = int(startpos + (i * skipsize))

            # Exit the loop if the position is beyond the end of the file
            if (pos > meta['npoints']-1):
                break;
                
            if pos<0: pos = 0

            # read from the file
            fh.seek(pos*4)
            val = struct.unpack("f",fh.read(4))

            # calculate the datapoint time
            timestamp = int(meta['start_time'] + pos * meta['interval'])

            # add to the data array if its not a nan value
            if not math.isnan(val[0]):
                data.append([timestamp*1000,val[0]])

            i += 1
        
        return data

    def lastvalue(self,filename):
        # If meta data file does not exist then exit
        meta = self.get_meta(filename)
        if not meta: return False
        
        meta['npoints'] = self.get_npoints(filename)
        
        if filename in self.lastvalue_cache:
            return self.lastvalue_cache[filename]
        
        size = os.stat(self.datadir+filename+".dat").st_size
        
        if size>=4:
            fh = open(self.datadir+filename+".dat","rb")
            fh.seek(size-4)
            val = struct.unpack("f",fh.read(4))
            self.lastvalue_cache[filename] = val[0]
            return val[0]
        
        return False        
        
    def pipe(self,filename):
    
        meta = self.get_meta(filename)
        if not meta:
            return False
        meta['npoints'] = self.get_npoints(filename)
        
        data = []
        pos = 0
        fh = open(self.datadir+filename+".dat","rb")
        while pos<meta['npoints']:

            # read from the file
            # fh.seek(pos*4)
            val = struct.unpack("f",fh.read(4))

            # calculate the datapoint time
            # timestamp = int(meta['start_time'] + pos * meta['interval'])

            # add to the data array if its not a nan value
            #if not math.isnan(val[0]):
            # data.append([timestamp*1000,val[0]])
            data.append(val[0])
            pos += 1
        
        return data
    
     
    def get_npoints(self,filename):

        bytesize = 0
        
        if os.path.isfile(self.datadir+filename+".dat"):
            bytesize += os.stat(self.datadir+filename+".dat").st_size
            
        if filename in self.buffers:
            bytesize += len(self.buffers[filename])
            
        return int(math.floor(bytesize / 4.0))
    
    
    def get_meta(self,filename):
    
        # Load metadata from cache if it exists
        if filename in self.metadata_cache:
            return self.metadata_cache[filename]
            
        elif os.path.isfile(self.datadir+filename+".meta"):
            # Open and read meta data file
            # The start_time and interval are saved as two consequative unsigned integers
            fh = open(self.datadir+filename+".meta","rb")
            tmp = struct.unpack("IIII",fh.read(16))
            fh.close()
            
            meta = {'start_time': tmp[3], 'interval': tmp[2]}
            
            # Save to metadata_cache so that we dont need to open the file next time
            self.metadata_cache[filename] = meta
            return meta
        else:
            return False
    
    
    def create_meta(self,filename,meta):
        # Create meta data file
        fh = open(self.datadir+filename+".meta","wb")
        fh.write(struct.pack("I",0))
        fh.write(struct.pack("I",0))
        fh.write(struct.pack("I",meta['interval']))
        fh.write(struct.pack("I",meta['start_time']))
        fh.close()
        
        # Save metadata to cache
        self.metadata_cache[filename] = meta

