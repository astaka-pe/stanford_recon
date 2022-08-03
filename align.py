import numpy as np
import open3d as o3d
import argparse

def get_parser():
    parser = argparse.ArgumentParser(description="align")
    parser.add_argument("-i", "--input", type=str, required=True)
    parser.add_argument("--para", type=str, default="0 0 0 0 0 0 1")
    args = parser.parse_args()
    return args

def quat_to_rm(quat):
    x, y, z, w = quat
    rm = np.zeros((3, 3))
    rm[0, 0] = x**2 - y**2 - z**2 + w**2
    rm[0, 1] = 2 * (x*y - z*w)
    rm[0, 2] = 2 * (x*z + y*w)
    rm[1, 0] = 2 * (x*y + z*w)
    rm[1, 1] = -x**2 + y**2 - z**2 + w**2
    rm[1, 2] = 2 * (y*z - x*w)
    rm[2, 0] = 2 * (x*z - y*w)
    rm[2, 1] = 2 * (y*z + x*w)
    rm[2, 2] = -x**2 - y**2 + z**2 + w**2
    return rm

def main():
    args = get_parser()
    pcd = o3d.io.read_point_cloud(args.input)
    para = args.para.split(" ")
    para = [float(p) for p in para]
    trans = np.array(para[:3])
    quat = np.array(para[3:])
    
    R = quat_to_rm(quat)
    pcd.points = o3d.utility.Vector3dVector((R @ np.asarray(pcd.points).T).T + trans.reshape(-1, 3))
    o3d.io.write_point_cloud("{}-aligned.ply".format(args.input.split(".")[0]), pcd, True)

if __name__ == "__main__":
    main()