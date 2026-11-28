import os, sys, time, json
from PIL import Image
import torch
import tsr.models.tokenizers.image
tsr.models.tokenizers.image.hf_hub_download=lambda **kw:os.environ['WSC_DINO_CFG']
from tsr.system import TSR
torch.set_num_threads(min(8,os.cpu_count() or 4))
start=time.monotonic()
def status(msg):print(round(time.monotonic()-start,1),msg,flush=True)
im=Image.open(sys.argv[1]).convert('RGB')
im.thumbnail((458,458), Image.Resampling.LANCZOS)
gray=im.getpixel((2,2))
square=Image.new('RGB',(512,512),gray)
square.paste(im,((512-im.width)//2,(512-im.height)//2))
square.save(sys.argv[2]+'.input.png')
status('loading pinned upstream model using weights_only')
model=TSR.from_pretrained(os.environ['WSC_WEIGHTS'],config_name='config.yaml',weight_name='model.ckpt').eval()
model.renderer.set_chunk_size(16384)
status('infer')
with torch.inference_mode():
 code=model([square],device='cpu')
 status('extract')
 mesh=model.extract_mesh(code,has_vertex_color=True,resolution=int(os.getenv('WSC_RES','144')),threshold=float(os.getenv('WSC_DENSITY','25')))[0]
 mesh.export(sys.argv[2])
 status(json.dumps({'vertices':len(mesh.vertices),'faces':len(mesh.faces),'bounds':mesh.bounds.tolist(),'watertight':mesh.is_watertight}))
