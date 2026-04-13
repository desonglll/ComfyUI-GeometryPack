# import sys
# print("[geompack] loading...", file=sys.stderr, flush=True)
# # from comfy_env import register_nodes
# # print("[geompack] calling register_nodes", file=sys.stderr, flush=True)

# # NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS = register_nodes()


# from comfy_dynamic_widgets import write_mappings
# write_mappings(NODE_CLASS_MAPPINGS, __file__)

# WEB_DIRECTORY = "./web"
# __all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']


import sys
from pathlib import Path

print("[geompack] Manual loading starting...", file=sys.stderr, flush=True)

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

try:
    from .nodes.blender import NODE_CLASS_MAPPINGS as B_NODES, NODE_DISPLAY_NAME_MAPPINGS as B_DISP
    from .nodes.gpu import NODE_CLASS_MAPPINGS as G_NODES, NODE_DISPLAY_NAME_MAPPINGS as G_DISP
    from .nodes.main import NODE_CLASS_MAPPINGS as M_NODES, NODE_DISPLAY_NAME_MAPPINGS as M_DISP
    
    NODE_CLASS_MAPPINGS.update(B_NODES)
    NODE_CLASS_MAPPINGS.update(G_NODES)
    NODE_CLASS_MAPPINGS.update(M_NODES)
    
    NODE_DISPLAY_NAME_MAPPINGS.update(B_DISP)
    NODE_DISPLAY_NAME_MAPPINGS.update(G_DISP)
    NODE_DISPLAY_NAME_MAPPINGS.update(M_DISP)

    for class_name in list(NODE_CLASS_MAPPINGS.keys()):
        if "Remesh" in class_name:
            NODE_CLASS_MAPPINGS["GeomPackRemesh"] = NODE_CLASS_MAPPINGS[class_name]
            print(f"[geompack] Aliasing {class_name} to GeomPackRemesh", file=sys.stderr)

except Exception as e:
    print(f"[geompack] Error during manual registration: {e}", file=sys.stderr)

WEB_DIRECTORY = "./web"
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']

print(f"[geompack] Load complete. Registered {len(NODE_CLASS_MAPPINGS)} nodes.", file=sys.stderr)