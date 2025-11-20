"""
Preview two meshes side by side with VTK.js with synchronized cameras.

Displays two meshes in an interactive VTK.js viewer with real-time
bidirectional camera synchronization.
"""

import trimesh as trimesh_module
import os
import tempfile
import uuid

try:
    import folder_paths
    COMFYUI_OUTPUT_FOLDER = folder_paths.get_output_directory()
except:
    COMFYUI_OUTPUT_FOLDER = None


class PreviewMeshVTKSideBySideNode:
    """
    Preview two meshes side by side with VTK.js with synchronized cameras.

    Displays two meshes in separate viewports with real-time bidirectional
    camera synchronization for easy comparison.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mesh_left": ("TRIMESH",),
                "mesh_right": ("TRIMESH",),
            },
        }

    RETURN_TYPES = ()
    OUTPUT_NODE = True
    FUNCTION = "preview_side_by_side"
    CATEGORY = "geompack/visualization"

    def preview_side_by_side(self, mesh_left, mesh_right):
        """
        Export both meshes to STL and prepare for VTK.js side-by-side preview.

        Args:
            mesh_left: Input trimesh_module.Trimesh object for left viewport
            mesh_right: Input trimesh_module.Trimesh object for right viewport

        Returns:
            dict: UI data for frontend widget
        """
        print(f"[PreviewMeshVTKSideBySide] Left mesh: {len(mesh_left.vertices)} vertices, {len(mesh_left.faces)} faces")
        print(f"[PreviewMeshVTKSideBySide] Right mesh: {len(mesh_right.vertices)} vertices, {len(mesh_right.faces)} faces")

        # Generate unique filenames
        filename_left = f"preview_vtk_left_{uuid.uuid4().hex[:8]}.stl"
        filename_right = f"preview_vtk_right_{uuid.uuid4().hex[:8]}.stl"

        # Use ComfyUI's output directory
        if COMFYUI_OUTPUT_FOLDER:
            filepath_left = os.path.join(COMFYUI_OUTPUT_FOLDER, filename_left)
            filepath_right = os.path.join(COMFYUI_OUTPUT_FOLDER, filename_right)
        else:
            filepath_left = os.path.join(tempfile.gettempdir(), filename_left)
            filepath_right = os.path.join(tempfile.gettempdir(), filename_right)

        # Export left mesh to STL
        try:
            mesh_left.export(filepath_left, file_type='stl')
            print(f"[PreviewMeshVTKSideBySide] Left mesh exported to: {filepath_left}")
        except Exception as e:
            print(f"[PreviewMeshVTKSideBySide] Left mesh export failed: {e}")
            # Fallback to OBJ
            filename_left = filename_left.replace('.stl', '.obj')
            filepath_left = filepath_left.replace('.stl', '.obj')
            mesh_left.export(filepath_left, file_type='obj')
            print(f"[PreviewMeshVTKSideBySide] Left mesh exported to OBJ: {filepath_left}")

        # Export right mesh to STL
        try:
            mesh_right.export(filepath_right, file_type='stl')
            print(f"[PreviewMeshVTKSideBySide] Right mesh exported to: {filepath_right}")
        except Exception as e:
            print(f"[PreviewMeshVTKSideBySide] Right mesh export failed: {e}")
            # Fallback to OBJ
            filename_right = filename_right.replace('.stl', '.obj')
            filepath_right = filepath_right.replace('.stl', '.obj')
            mesh_right.export(filepath_right, file_type='obj')
            print(f"[PreviewMeshVTKSideBySide] Right mesh exported to OBJ: {filepath_right}")

        # Calculate metadata for left mesh
        bounds_left = mesh_left.bounds
        extents_left = mesh_left.extents
        is_watertight_left = mesh_left.is_watertight

        # Calculate metadata for right mesh
        bounds_right = mesh_right.bounds
        extents_right = mesh_right.extents
        is_watertight_right = mesh_right.is_watertight

        # Return metadata for frontend widget
        ui_data = {
            "mesh_left_file": [filename_left],
            "mesh_right_file": [filename_right],
            "vertex_count_left": [len(mesh_left.vertices)],
            "vertex_count_right": [len(mesh_right.vertices)],
            "face_count_left": [len(mesh_left.faces)],
            "face_count_right": [len(mesh_right.faces)],
            "bounds_min_left": [bounds_left[0].tolist()],
            "bounds_max_left": [bounds_left[1].tolist()],
            "bounds_min_right": [bounds_right[0].tolist()],
            "bounds_max_right": [bounds_right[1].tolist()],
            "extents_left": [extents_left.tolist()],
            "extents_right": [extents_right.tolist()],
            "is_watertight_left": [bool(is_watertight_left)],
            "is_watertight_right": [bool(is_watertight_right)],
        }

        print(f"[PreviewMeshVTKSideBySide] Left mesh: watertight={is_watertight_left}")
        print(f"[PreviewMeshVTKSideBySide] Right mesh: watertight={is_watertight_right}")

        return {"ui": ui_data}


NODE_CLASS_MAPPINGS = {
    "GeomPackPreviewMeshVTKSideBySide": PreviewMeshVTKSideBySideNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GeomPackPreviewMeshVTKSideBySide": "Preview Mesh Side-by-Side (VTK)",
}
