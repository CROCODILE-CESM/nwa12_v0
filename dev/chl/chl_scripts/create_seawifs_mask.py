import xesmf as xe
import xarray as xr
from pathlib import Path
from datetime import date


def main():

    # Get Data

    # Get Land Mask
    LandWaterMask = xr.open_dataset("/glade/u/home/manishrv/documents/croc/dev/chl/SeaWIFS_MOM6/ncfiles/LandWater15ARC.nc")

    # Get a SEAWIFS file (only need the coordinates)
    path_chl = Path('/glade/u/home/manishrv/scratch/chl')
    file_chl = 'SEASTAR_SEAWIFS_GAC.19971001_20101031.L3m.MC.CHL.chlor_a.9km.nc'
    ds_chl = xr.open_dataset(path_chl/file_chl)


    # Chunk it
    LandWaterMask = LandWaterMask.chunk({'lat': 500, 'lon': 500})
    ds_chl = ds_chl.chunk({'lat': 500, 'lon': 500})


    # Regrid to CHL

    Mask_lores = LandWaterMask['LandWater'].sel(
                lon=ds_chl['lon'],
                lat=ds_chl['lat'],method='nearest').astype('int')
    ## Create a corresponding mask of all ocean areas (shallow=0,shelf=6,deep=7)
    Ocean_lores = xr.where(Mask_lores==0,1,0)
    Ocean_lores = xr.where(Mask_lores>=6,1,Ocean_lores)
    Ocean_lores = Ocean_lores.astype('int')

    ## Create the reciprocal land mask
    Land_lores = (1 - Ocean_lores).astype('int')

    # Put the masks in a dataset
    ds_out = xr.Dataset({"LandWater" : Mask_lores})

    ds_out['Ocean'] = Ocean_lores
    ds_out['Ocean'].attrs['long_name'] = 'Ocean Mask'
    ds_out['Ocean'].attrs['flag_values'] = '0, 1'
    ds_out['Ocean'].attrs['flag_meanings'] = '0=Land or Inland Water, 1=Ocean'

    ds_out['Land'] = Land_lores
    ds_out['Land'].attrs['long_name'] = 'Land Mask'
    ds_out['Land'].attrs['flag_values'] = '0, 1'
    ds_out['Land'].attrs['flag_meanings'] = '1=Land or Inland Water, 0=Ocean'

    # Tweak the coordinates to agree exactly with SeaWIFS 
    ds_out.coords['lon'] = ds_chl['lon']
    ds_out.coords['lat'] = ds_chl['lat']

    # Add a history attribute
    today = date.today()
    dstr = today.strftime("%Y-%m-%d")
    astr = 'Created ' + dstr + ' from input file ' + "/glade/u/home/manishrv/documents/croc/dev/chl/SeaWIFS_MOM6/ncfiles/LandWater15ARC.nc"
    astr
    ds_out.attrs['history'] = astr

    fileout = '/glade/u/home/manishrv/documents/croc/dev/chl/SeaWIFS_MOM6/ncfiles/NEW_LandWater_SeaWIFS.nc'
    ds_out.to_netcdf(fileout)




if __name__ == "__main__":
    main()