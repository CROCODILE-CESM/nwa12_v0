from CrocoDash.grid import Grid
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import scipy
from datetime import datetime
from pathlib import Path
from gen_chl_netcdf_file import gen_chl_dummy_dataset
def super_sample_grid(ocn_qlat, ocn_qlon, ocn_mask, src_nj, src_ni):
    nj, ni = ocn_mask.shape
    fac = 1
    while fac*nj<src_nj and fac*ni<src_ni:
        fac += 1
    lon = np.zeros( (nj,fac,ni,fac) )
    lat = np.zeros( (nj,fac,ni,fac) )
    mask = np.zeros( (nj,fac,ni,fac) )
    for j in range(fac):
        ya = ( 2*j+1 ) / ( 2*fac )
        yb = 1. - ya
        for i in range(fac):
            xa = ( 2*i+1 ) / ( 2*fac )
            xb = 1. - xa
            lon[:,j,:,i] = (  yb * ( xb * ocn_qlon[:-1,:-1] + xa * ocn_qlon[:-1,1:] )
                            + ya * ( xb * ocn_qlon[1:,:-1] + xa * ocn_qlon[1:,1:] ) )
            lat[:,j,:,i] = (  yb * ( xb * ocn_qlat[:-1,:-1] + xa * ocn_qlat[:-1,1:] )
                            + ya * ( xb * ocn_qlat[1:,:-1] + xa * ocn_qlat[1:,1:] ) )
    return lat, lon
def latlon2ji(src_lat, src_lon, lat, lon):
    nj, ni = len(src_lat), len(src_lon)
    src_x0 = int( ( src_lon[0] + src_lon[-1] )/2 + 0.5) - 180.
    j = np.maximum(0, np.floor( ( ( lat + 90. ) / 180. ) * nj - 0.5 ).astype(int))
    i = np.mod( np.floor( ( ( lon - src_x0 ) / 360. ) * ni - 0.5 ), ni ).astype(int)
    jp1 = np.minimum(nj-1, j+1)
    ip1 = np.mod(i+1, ni)
    return j,i,jp1,ip1

def super_interp(src_lat, src_lon, data, spr_lat, spr_lon):
    nj, ni = data.shape
    dy, dx = 180./nj, 360./ni
    j0, i0, j1, i1 = latlon2ji(src_lat, src_lon, spr_lat, spr_lon)
    def ydist(lat0, lat1):
        return np.abs( lat1-lat0 )
    def xdist(lon0, lon1):
        return np.abs( np.mod((lon1-lon0)+180, 360) - 180 )
    w_e = xdist( src_lon[i0], spr_lon) / dx
    w_w = 1. - w_e
    w_n = ydist( src_lat[j0], spr_lat) / dy
    w_s = 1. - w_n
    return ( w_s*w_w * data[j0,i0] + w_n*w_e * data[j1,i1] ) + ( w_n*w_w * data[j1,i0] + w_s*w_e * data[j0,i1] )
def fill_missing_data(idata, mask, verbose=True, maxiter=0, debug=False, stabilizer=1.e-14):
    """
    Returns data with masked values objectively interpolated except where mask==0.
    
    Arguments:
    data - np.ma.array with mask==True where there is missing data or land.
    mask - np.array of 0 or 1, 0 for land, 1 for ocean.
    
    Returns a np.ma.array.
    """
    nj,ni = idata.shape
    fdata = idata.filled(0.) # Working with an ndarray is faster than working with a masked array
    if debug:
        plt.figure(); plt.pcolormesh(mask); plt.title('mask'); plt.colorbar();
        #plt.figure(); plt.pcolormesh(idata.mask); plt.title('idata.mask'); plt.colorbar();
        plt.figure(); plt.pcolormesh(idata); plt.title('idata'); plt.colorbar();
        plt.figure(); plt.pcolormesh(idata.filled(3.)); plt.title('idata.filled'); plt.colorbar();
        plt.figure(); plt.pcolormesh(idata.filled(3.)); plt.title('fdata'); plt.colorbar();
    missing_j, missing_i = np.where( idata.mask & (mask>0) )
    n_missing = missing_i.size
    if verbose:
        print('Data shape: %i x %i = %i with %i missing values'%(nj, ni, nj*ni, np.count_nonzero(idata.mask)))
        print('Mask shape: %i x %i = %i with %i land cells'%(mask.shape[0], mask.shape[1],
                                                                 np.prod(mask.shape), np.count_nonzero(1-mask)))
        print('Data has %i missing values in ocean'%(n_missing))
        print('Data range: %g .. %g '%(idata.min(),idata.max()))
    # ind contains column of matrix/row of vector corresponding to point [j,i]
    ind = np.zeros( fdata.shape, dtype=int ) - int(1e6)
    ind[missing_j,missing_i] = np.arange( n_missing )
    if verbose: print('Building matrix')
    A = scipy.sparse.lil_matrix( (n_missing, n_missing) )
    b = np.zeros( (n_missing) )
    ld = np.zeros( (n_missing) )
    A[range(n_missing),range(n_missing)] = 0.
    if verbose: print('Looping over cells')
    for n in range(n_missing):
        j,i = missing_j[n],missing_i[n]
        im1 = ( i + ni - 1 ) % ni
        ip1 = ( i + 1 ) % ni
        jm1 = max( j-1, 0)
        jp1 = min( j+1, nj-1)
        if j>0 and mask[jm1,i]>0:
            ld[n] -= 1.
            ij = ind[jm1,i]
            if ij>=0:
                A[n,ij] = 1.
            else:
                b[n] -= fdata[jm1,i]
        if mask[j,im1]>0:
            ld[n] -= 1.
            ij = ind[j,im1]
            if ij>=0:
                A[n,ij] = 1.
            else:
                b[n] -= fdata[j,im1]
        if mask[j,ip1]>0:
            ld[n] -= 1.
            ij = ind[j,ip1]
            if ij>=0:
                A[n,ij] = 1.
            else:
                b[n] -= fdata[j,ip1]
        if j<nj-1 and mask[jp1,i]>0:
            ld[n] -= 1.
            ij = ind[jp1,i]
            if ij>=0:
                A[n,ij] = 1.
            else:
                b[n] -= fdata[jp1,i]
        if j==nj-1 and mask[j,ni-1-i]>0: # Tri-polar fold
            ld[n] -= 1.
            ij = ind[j,ni-1-i]
            if ij>=0:
                A[n,ij] = 1.
            else:
                b[n] -= fdata[j,ni-1-i]
    if debug:
        tmp = np.zeros((nj,ni)); tmp[ missing_j, missing_i ] = b
        plt.figure(); plt.pcolormesh(tmp); plt.title('b (initial)'); plt.colorbar();
    # Set leading diagonal
    b[ld>=0] = 0.
    A[range(n_missing),range(n_missing)] = ld - stabilizer
    if debug:
        tmp = np.zeros((nj,ni)); tmp[ missing_j, missing_i ] = b
        plt.figure(); plt.pcolormesh(tmp); plt.title('b (final)'); plt.colorbar();
        tmp = np.ones((nj,ni)); tmp[ missing_j, missing_i ] = A.diagonal()
        plt.figure(); plt.pcolormesh(tmp); plt.title('A[i,i]'); plt.colorbar();
    if verbose: print('Matrix constructed')
    A = scipy.sparse.csr_matrix(A)
    if verbose: print('Matrix converted')
    new_data = np.ma.array( fdata, mask=(mask==0))
    if maxiter is None:
        x,info = scipy.sparse.linalg.bicg(A, b)
    elif maxiter==0:
        x = scipy.sparse.linalg.spsolve(A, b)
    else:
        x,info = scipy.sparse.linalg.bicg(A, b, maxiter=maxiter)
    if verbose: print('Matrix inverted')
    new_data[missing_j,missing_i] = x
    return new_data
def main():
    grid = Grid.from_supergrid("/glade/u/home/manishrv/croc_input/panama-chl/ocnice/ocean_hgrid_panama1_889d3f.nc")
    ocn_mask = xr.open_dataset('/glade/u/home/manishrv/croc_input/panama-chl/ocnice/ocean_topog_panama1_889d3f.nc')['mask']
    ocn_nj, ocn_ni = ocn_mask.shape

    src_nc = xr.open_dataset('/glade/work/gmarques/cesm/tx2_3/chlorophyll/ncfiles/SeaWIFS.L3m_MC_CHL_chlor_a_0.25deg.nc')
    src_data = src_nc.variables['chlor_a']
    src_nj, src_ni = src_data.shape[-2], src_data.shape[-1]
    src_lon = src_nc.variables[src_data.dimensions[-1]]
    src_lat = src_nc.variables[src_data.dimensions[-2]]
    src_lat = ((np.arange(src_nj)+0.5)/src_nj - 0.5)*180. # Recompute as doubles
    src_x0 = int( ( src_lon[0] + src_lon[-1] )/2 + 0.5) - 180.
    src_lon = ((np.arange(src_ni)+0.5)/src_ni)*360.+src_x0 # Recompute as doubles
    src_qlat = ((np.arange(src_nj+1))/src_nj - 0.5)*180. # For plotting
    src_qlon = ((np.arange(src_ni+1))/src_ni)*360.+src_x0 # For plotting

    spr_lat, spr_lon = super_sample_grid(grid.qlat, grid.qlon, ocn_mask, src_nj, src_ni)
    y, x = src_lat[0], src_lon[0]
    output_path = Path(__file__).resolve().parent.parent /"ncfiles"/ "NEWseawifs-clim-1997-2010-tx0.66v1.nc"
    ds = gen_chl_dummy_dataset(output_path)
    chla_tx06 = xr.open_dataset('/glade/u/home/manishrv/documents/croc/dev/chl/SeaWIFS_MOM6/ncfiles/seawifs-clim-1997-2010-tx0.66v1.nc')
    chlor_a = chla_tx06.variables['CHL_A'][:]

    for t in range(src_data.shape[0]):
    #for t in range(1):
        q_int = super_interp(src_lat, src_lon, src_data[t,::-1,:], spr_lat, spr_lon)
        q_int = q_int.swapaxes(1,2).reshape((ocn_nj,ocn_ni,q_int.shape[3]*q_int.shape[-1])).mean(axis=-1)
        q = q_int * ocn_mask
        chlor_a[t,:] = fill_missing_data(q, ocn_mask)
    # Global attrs
    chla_tx06.title = 'Chlorophyll Concentration, OCI Algorithm, interpolated and objectivelly filled to tx0.66v1'
    chla_tx06.repository = 'https://github.com/NCAR/SeaWIFS_MOM6'
    chla_tx06.authors = 'Gustavo Marques (gmarques@ucar.edu) and Frank Bryan (bryan@ucar.edu )'
    chla_tx06.date = datetime.now().isoformat()

    chla_tx06.variables['CHL_A'][:,:,:] = chlor_a[:,:,:]
    chla_tx06.variables['LON'][:] = grid.tlon[grid.ny,:]
    chla_tx06.variables['LAT'][:] = grid.tlat[:,grid.nx]

    chla_tx06.close()
if __name__ == "__main__":
    main()