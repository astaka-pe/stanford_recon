import numpy as np
import pymeshlab as ml
import open3d as o3d
import argparse
import os
import matplotlib.pyplot as plt

def get_parser():
    parser = argparse.ArgumentParser(description="align")
    parser.add_argument("-i", "--input", type=str, nargs="*", required=True)
    parser.add_argument("--invert", type=int, default=0)
    parser.add_argument("-o", "--output", type=str, required=True)
    args = parser.parse_args()
    return args

def main():
    args = get_parser()
    ms = ml.MeshSet()
    """ Read ply files """
    merge_vs = np.zeros((0, 3))
    for file in args.input:
        ms.load_new_mesh(file)
        if merge_vs.shape[0] == 0:
            merge_vs = ms.current_mesh().vertex_matrix()
        else:
            merge_vs = np.concatenate([merge_vs, ms.current_mesh().vertex_matrix()])
    rec_pcd = ml.Mesh(vertex_matrix=merge_vs)
    ms.add_mesh(mesh=rec_pcd)
    
    """ Normal estimation """
    ms.apply_filter("compute_normals_for_point_sets", k=50)
    os.makedirs("data/{}/recon/".format(args.output, args.output), exist_ok=True)
    ms.save_current_mesh("data/{}/recon/{}-merge.ply".format(args.output, args.output), save_vertex_normal=True)  

    """ Poisson surface reconstruction """
    rec_pcd = o3d.io.read_point_cloud("data/{}/recon/{}-merge.ply".format(args.output, args.output))
    mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(rec_pcd, depth=9)
    
    if args.invert:
        # invert orientation
        mesh.triangles = o3d.utility.Vector3iVector(np.asarray(mesh.triangles)[:, [0, 2, 1]])
    
    o3d.io.write_triangle_mesh("data/{}/recon/{}-recon.obj".format(args.output, args.output), mesh)

    """ Remove low density vertices (open3d) """
    densities = np.asarray(densities)
    density_colors = plt.get_cmap('plasma')(
    (densities - densities.min()) / (densities.max() - densities.min()))
    density_mesh = o3d.geometry.TriangleMesh()
    density_mesh.vertices = mesh.vertices
    density_mesh.triangles = mesh.triangles
    density_mesh.triangle_normals = mesh.triangle_normals
    density_mesh.vertex_colors = o3d.utility.Vector3dVector(density_colors[:, :3])
    vertices_to_remove = densities < np.quantile(densities, 0.01)
    mesh.remove_vertices_by_mask(vertices_to_remove)

    o3d.io.write_triangle_mesh("data/{}/recon/{}-final.obj".format(args.output, args.output), mesh)
    o3d.io.write_triangle_mesh("data/{}/recon/{}-density.obj".format(args.output, args.output), density_mesh)
    
    """ Remove low density vertices (meshlab) """
    # ms.apply_filter("estimate_radius_from_density")
    # ms.apply_filter("per_vertex_quality_function", q="rad", normalize=True)
    # ms.save_current_mesh("{}-final.ply".format(args.output), save_vertex_radius=True)
    # import pdb;pdb.set_trace()
    
if __name__ == "__main__":
    main()