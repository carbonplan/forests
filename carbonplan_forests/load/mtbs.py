import fsspec
import numpy as np
import xarray as xr

from .. import setup
from ..utils import rowcol_to_latlon


def mtbs(store='gcs', tlim=None, res=64000, coarsen=None):
    path = setup.loading(store)
    mapper = fsspec.get_mapper((path / f'processed/mtbs/conus/{res}m/monthly_raster.zarr').as_uri())
    mtbs = xr.open_zarr(mapper)
    mtbs['x'] = range(len(mtbs['x']))
    mtbs['y'] = range(len(mtbs['y']))
    mtbs = mtbs.drop('x')
    mtbs = mtbs.drop('y')

    rows = np.tile(mtbs['y'].values[:,np.newaxis], [1, len(mtbs['x'].values)])
    cols = np.tile(mtbs['x'].values, [len(mtbs['y'].values), 1])
    lat, lon = rowcol_to_latlon(rows.flatten(), cols.flatten(), res)
    mtbs['lat'] = (['y', 'x'], np.asarray(lat).reshape(len(mtbs['y']), len(mtbs['x'])))
    mtbs['lon'] = (['y', 'x'], np.asarray(lon).reshape(len(mtbs['y']), len(mtbs['x'])))

    if tlim:
        tlim = list(map(str, tlim))
        mtbs = mtbs.sel(time=slice(*tlim))

    if coarsen:
        mtbs = mtbs.coarsen(x=coarsen, y=coarsen, boundary='trim').mean()
    
    mtbs.load()
    return mtbs