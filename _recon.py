import numpy as np
import open3d as o3d
import pymeshlab as ml
import argparse
import matplotlib.pyplot as plt

def get_parser():
    parser = argparse.ArgumentParser(description="align")
    parser.add_argument("-i", "--input", type=str, nargs="*", required=True)
    parser.add_argument("-o", "--output", type=str, required=True)
    args = parser.parse_args()
    return args

def main():
    args = get_parser()
    rec_pcd = o3d.geometry.PointCloud()
    """ Read ply files """
    for file in args.input:
        pcd = o3d.io.read_point_cloud(file)
        if len(np.asarray(rec_pcd.points)) == 0:
            rec_pcd.points = pcd.points
        else:
            rec_pcd.points = o3d.utility.Vector3dVector(np.concatenate([np.asarray(rec_pcd.points), np.asarray(pcd.points)]))
    
    """ Normal estimation """
    rec_pcd.normals = o3d.utility.Vector3dVector(np.zeros((1, 3)))
    #search_param = o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=50)
    search_param = o3d.geometry.KDTreeSearchParamKNN(50)
    rec_pcd.estimate_normals(search_param=search_param, fast_normal_computation=False)
    rec_pcd.estimate_normals(search_param=search_param, fast_normal_computation=False)
    
    """ Poisson surface reconstruction """
    # mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(rec_pcd, depth=9)
    # densities = np.asarray(densities)
    # density_colors = plt.get_cmap('plasma')(
    # (densities - densities.min()) / (densities.max() - densities.min()))
    # density_mesh = o3d.geometry.TriangleMesh()
    # density_mesh.vertices = mesh.vertices
    # density_mesh.triangles = mesh.triangles
    # density_mesh.triangle_normals = mesh.triangle_normals
    # #import pdb;pdb.set_trace()
    # density_mesh.vertex_colors = o3d.utility.Vector3dVector(density_colors[:, :3])
    """ Remove low density vertices """
    # vertices_to_remove = densities < np.quantile(densities, 0.06)
    # mesh.remove_vertices_by_mask(vertices_to_remove)

    # o3d.io.write_triangle_mesh("{}-recon.obj".format(args.output), mesh)
    # o3d.io.write_triangle_mesh("{}-density.obj".format(args.output), density_mesh)

    """ alpha reconstruction """
    # radii = [0.005, 0.01, 0.02, 0.04]
    # mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(rec_pcd, o3d.utility.DoubleVector(radii))

    o3d.io.write_point_cloud("{}-recon.ply".format(args.output), rec_pcd)
    # o3d.io.write_triangle_mesh("{}-recon.obj".format(args.output), mesh)
    
if __name__ == "__main__":
    main()