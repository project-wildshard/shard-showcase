import numpy as np
import torch
from skimage.measure import marching_cubes as sk_mc
def marching_cubes(field,level):
    vertices,faces,_,_=sk_mc(field.detach().cpu().numpy(),level=level,allow_degenerate=False)
    # tsr.MarchingCubeHelper reverses the torchmcubes ZYX convention.
    return torch.from_numpy(vertices[:,::-1].copy()),torch.from_numpy(faces.astype(np.int64))
