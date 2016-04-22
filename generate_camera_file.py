import sys
import os
import getpass
from collections import OrderedDict
import datetime

def camera(fname,
           camera_options={}, geometry_options={},
           sampling_options={}, results_options={}, 
           remove=[], comment=None, verbose=False):
           
    """
    refer to wikispace.librat.com for full definitions
    
    INPUT
    -----
    
    fname: path to save camera file
    
    results: default None, str
    If this is None then a random name is generated, otherwise
    str is used.
    
    remove: default [], list
    list of commands as strings in the librat format that
    are to be not included in the camera file
    
    comment: default None, str
    a comment to inlcude at the beigging of the camera file
    e.g. associtated light file etc.
    """
    
    if os.path.isfile(fname):
        R = raw_input('this camera exists, overwrite? (y/n)').lower()
        if R != 'y':
            sys.exit()
    
    camera = OrderedDict()
    camera['camera.name'] = 'simple camera'       

    for K, V in camera_options.items():
        camera[K] = V   
    
    geometry = OrderedDict()
    geometry['geometry.perspective'] = True
    geometry['geometry.azimuth'] =  0.0
    geometry['geometry.zenith'] =  0.0
    geometry['geometry.twist'] = 0.0
    geometry['geometry.lookAt'] = [0, 0, 0]
    geometry['geometry.idealArea'] = 2
    geometry['geometry.boomLength'] = 10.

    for K, V in geometry_options.items():
        geometry[K] = V
                
    sampling = OrderedDict()
    sampling['samplingCharacteristics.nPixels'] = 262144
    sampling['samplingCharacteristics.rpp'] = 4
                
    for K, V in sampling_options.items():
        sampling[K] = V
     
    ### setting results
    if 'oname' in results_options.keys():
        oname = results_options['oname']
    else:
        oname = '-'.join(camera['camera.name'].split()) + '_' + datetime.datetime.now().strftime("%y-%m-%d_%H:%M:%S")
    
    results = OrderedDict()
    results['result.integral.mode'] = 'scattering order'
    results['result.integral.format'] = 'ascii'
    results['result.image'] = oname + '.hips'
    results['result.integral'] = oname + '.results'
        
    ### concatenate settings
    camera_settings = OrderedDict(camera.items() + 
                                  geometry.items() +
                                  sampling.items() +
                                  results.items())
                                  
    for drop in remove:
        del camera_settings[drop]
                                    
    with open(fname, 'w') as cam:
    
        cam.write('camera {\n')
        cam.write('\n')
                
        cam.write('# camera location: {}\n'.format(fname))
        cam.write('# created by: {}\n'.format(getpass.getuser()))
        
        if comment is not None:
            for line in range((len(comment) // 75) + 1):
                cam.write('# ' + comment[line * 75: (line + 1) * 75] + '\n')
                
        cam.write('\n')
        
        for K, V in camera_settings.items():
            if isinstance(V, list):
                V = ','.join([str(v) for v in V])
            elif isinstance(V, str):
                V = '"{}"'.format(V)
            elif isinstance(V, bool):
                V = '{}'.format({True:'TRUE', False:'FALSE'}[V])
            cam.write('{} = {};\n'.format(K, V))
            if verbose: print '{} = {};\n'.format(K, V).strip()
        
        cam.write('}')
        
    return oname

if __name__ == '__main__':

    fname = sys.argv[1]
    
    if len(sys.argv) > 2:
        for i, arg in enumerate(sys.argv[2::2]):
            if arg == '--comment':
                comment = sys.argv[i + 3]
            else:
                print '{} not understood'.format(arg)
    
    camera(fname, comment=comment)