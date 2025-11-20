"""
Point to Mesh Distance Node - Compute distances from points to mesh surface
"""

import numpy as np


class PointToMeshDistanceNode:
    """
    Point to Mesh Distance - Compute distance field from point cloud/mesh to target mesh surface.

    For each vertex in the input (point cloud or mesh), finds the closest point on the
    target mesh surface and computes the distance. Returns the input geometry with a
    'distance' field added to vertex_attributes.

    Useful for proximity analysis, error measurements, and distance-based visualizations.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "target_mesh": ("TRIMESH",),
                "pointcloud": ("TRIMESH",),
            }
        }

    RETURN_TYPES = ("TRIMESH", "STRING")
    RETURN_NAMES = ("pointcloud", "info")
    FUNCTION = "compute_distance"
    CATEGORY = "geompack/distance"

    def compute_distance(self, target_mesh, pointcloud):
        """
        Compute distances from point cloud/mesh vertices to target mesh surface.

        Args:
            target_mesh: Target trimesh.Trimesh object to measure distance to
            pointcloud: Input point cloud or mesh (TRIMESH) to compute distances for

        Returns:
            tuple: (pointcloud_with_distance_field, info_string)
        """
        # Extract vertices from input (works for both mesh and point cloud)
        points = pointcloud.vertices

        # Determine if input is a mesh or point cloud
        is_mesh = len(pointcloud.faces) > 0
        input_type = "Mesh" if is_mesh else "Point Cloud"

        print(f"[PointToMeshDistance] Computing distances for {len(points):,} points")
        print(f"[PointToMeshDistance] Input: {input_type}")
        print(f"[PointToMeshDistance] Target Mesh: {len(target_mesh.vertices):,} vertices, {len(target_mesh.faces):,} faces")

        # Use trimesh's proximity query to find closest points and distances
        closest_points, distances, triangle_ids = target_mesh.nearest.on_surface(points)

        # Create a copy of the input to add distance field
        result = pointcloud.copy()

        # Add distance field to vertex attributes
        result.vertex_attributes['distance'] = distances.astype(np.float32)

        # Add metadata
        if not hasattr(result, 'metadata') or result.metadata is None:
            result.metadata = {}

        result.metadata['has_distance_field'] = True
        result.metadata['target_mesh_vertices'] = len(target_mesh.vertices)
        result.metadata['target_mesh_faces'] = len(target_mesh.faces)
        result.metadata['num_points'] = len(points)

        # Compute statistics for info string
        min_dist = float(np.min(distances))
        max_dist = float(np.max(distances))
        mean_dist = float(np.mean(distances))
        median_dist = float(np.median(distances))
        std_dist = float(np.std(distances))

        # Find percentiles
        percentile_25 = float(np.percentile(distances, 25))
        percentile_75 = float(np.percentile(distances, 75))
        percentile_95 = float(np.percentile(distances, 95))

        # Count points within certain distance thresholds
        threshold_01 = np.sum(distances < 0.1)
        threshold_05 = np.sum(distances < 0.5)
        threshold_10 = np.sum(distances < 1.0)

        info = f"""Point to Mesh Distance Field:

Input:
  {input_type}: {len(points):,} {'vertices' if is_mesh else 'points'}
  Target Mesh: {len(target_mesh.vertices):,} vertices, {len(target_mesh.faces):,} faces

Distance Statistics:
  Minimum: {min_dist:.6f}
  Maximum: {max_dist:.6f}
  Mean: {mean_dist:.6f}
  Median: {median_dist:.6f}
  Std Dev: {std_dist:.6f}

Percentiles:
  25th: {percentile_25:.6f}
  75th: {percentile_75:.6f}
  95th: {percentile_95:.6f}

Distance Distribution:
  < 0.1: {threshold_01:,} points ({100.0 * threshold_01 / len(points):.1f}%)
  < 0.5: {threshold_05:,} points ({100.0 * threshold_05 / len(points):.1f}%)
  < 1.0: {threshold_10:,} points ({100.0 * threshold_10 / len(points):.1f}%)

Output: {input_type} with 'distance' field in vertex_attributes
"""

        print(f"[PointToMeshDistance] Min: {min_dist:.6f}, Max: {max_dist:.6f}, Mean: {mean_dist:.6f}")
        print(f"[PointToMeshDistance] Distance field added to vertex_attributes['distance']")

        return (result, info)


# Node mappings
NODE_CLASS_MAPPINGS = {
    "GeomPackPointToMeshDistance": PointToMeshDistanceNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GeomPackPointToMeshDistance": "Point to Mesh Distance",
}
