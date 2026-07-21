;===============================================================================
; create data model domain file from GloFAS data file and add a mask
; to represent the domain of the caribeean regional example
;===============================================================================

newline = integertochar(10) ; create a newline character

;----- hard-coded input --------------------------------------------------------

; path_in=""
path_in =""
fn_in   = "/glade/u/home/manishrv/documents/croc/dev/runoff/ncl_required_fields_hgrid.nc"
fn_in1   = "/glade/u/home/manishrv/documents/croc/dev/runoff/glofas_runoff/GloFAS_little_nwa.nc"
fn_out  = "domain.roff.glofas_little_nwa_1.nc"

title       = "glofas runoff grid -- for use with the glofas runoff data in the NWA12 CESM configuration"
history     = "Created by " + systemfunc("whoami") + " " + systemfunc("date")
notes       = "glofas runoff domain data (Aug 2024), formatted for use in CESM"
; notes       = notes + newline + "Includes sort field where 1=>largest runoff value, 2=> 2nd largest runoff value,etc."
Conventions = "CF1.0"
Source      = "Glofas"

masked = 1

;-------------------------------------------------------------------------------

;-------------------------------------------------------------------------------
print_clock("reading "+fn_in)
;-------------------------------------------------------------------------------

fh_in = addfile(path_in+fn_in,"r")
fh_in1 = addfile(fn_in1,"r")

grid_dimsizes = getfiledimsizes(fh_in)
njp = grid_dimsizes(0)
nip = grid_dimsizes(1)
nj = grid_dimsizes(2)
ni = grid_dimsizes(3)
nv =    4 ; WARNING: hard-coded four verticies

pi = 4.0d * atan(1.0d)
deg2rad = pi/180.0d

dx      = 0.1d    ; WARNING: hard-coded for 0.1 degree
half_dx = 0.5d * dx


longitude=fh_in->tlon
latitude =fh_in->tlat
qlat     =fh_in->qlat
qlon     =fh_in->qlon
;dmask1 =fh_in->land_ocean_mask
dmask1 =fh_in->tmask
tmp =fh_in1->runoff(:,:,:)
runoff = dim_sum_n(tmp,0)
;-------------------------------------------------------------------------------
print_clock("create data")
;-------------------------------------------------------------------------------

xc    = new( (/nj,ni/)   , "double")
yc    = new( (/nj,ni/)   , "double")
xv    = new( (/nj,ni,nv/), "double")
yv    = new( (/nj,ni,nv/), "double")
area  = new( (/nj,ni/)   , "double")
dmask = new( (/nj,ni/)   , "integer")
;sort  = new( (/nj,ni/)   , "integer")
;fracl = new( (/nj,ni/)   , "double")


xc    = -999.
yc    = -999.
xv    = -999.
yv    = -999.
area  = -999.
dmask = 0
;order = -999
;fracl = -999.

;----- create mask data -----
;----- create mask data -----
dmask = 1
if (masked .ne.0) then
   dmask = where( runoff > 0.0, 1, 0)
end if

;----- create verticie data -----
do j=0,nj-1
   do i=0,ni-1
     yc(j,i)  = latitude(j,i)
     xc(j,i)  = longitude(j,i)

     yv(j,i,0) = qlat(j,i)
     yv(j,i,1) = qlat(j,i+1)
     yv(j,i,2) = qlat(j+1,i+1)
     yv(j,i,3) = qlat(j+1,i)

     xv(j,i,0) = qlon(j,i)
     xv(j,i,1) = qlon(j,i+1)
     xv(j,i,2) = qlon(j+1,i+1)
     xv(j,i,3) = qlon(j+1,i)

   end do
end do

;----- create area data using verticie data -----

sum_test = 0.0d
do j=0,nj-1
   y0 = sin(yv(j,0,0)*deg2rad) ; south
   y1 = sin(yv(j,0,3)*deg2rad) ; north
   do i=0,ni-1
      x0 = xv(j,i,0) ; west
      x1 = xv(j,i,1) ; east
      area(j,i) = (y1-y0)*(x1-x0)*deg2rad
      sum_test = sum_test+area(j,i)
   end do
end do
print_clock("sum_test/(4*pi) = "+sum_test/(4.0d*pi)  )

;=========================================================================================
; make a CESM data model domain file (fields are 2d)
;=========================================================================================

;-------------------------------------------------------------------------------
print_clock("create meta-data")
;-------------------------------------------------------------------------------

xc@bounds       = "xv"
xc@units        = "degrees_north"
xc@long_name    = "longitude of grid cell center"
xc@cartesian_axis = "X"
xc@axis = "X"
xc@point_spacing = "even"
delete(xc@_FillValue)
delete(xc@standard_name)

yc@bounds       = "yv"
yc@units        = "degrees_north"
yc@long_name    = "latitude of grid cell center"
yc@cartesian_axis = "Y"
yc@axis = "Y"
yc@point_spacing = "even"
delete(yc@_FillValue)
delete(yc@standard_name)

xv@units        = "degrees_north"
xv@long_name    = "longitude of grid cell verticies"
delete(xv@_FillValue)

yv@units        = "degrees_north"
yv@long_name    = "latitude of grid cell verticies"
delete(yv@_FillValue)

dmask@coordinates = "yc xc"
dmask@comment     = "0 value if cell is not active"
dmask@note        = "unitless"
dmask@long_name   = "domain mask"
delete(dmask@_FillValue)

area@coordinates = "yc xc"
area@units       = "radian2"
area@long_name   = "area of grid cell in radians squared"
delete(area@_FillValue)

;fracl@coordinates = "yc xc"
;fracl@note        = "unitless, range = [0,1]"
;fracl@long_name   = "fraction of land in cell"
;delete(fracl@_FillValue)

gAtt = True
gAtt@notes       = notes
gAtt@history     = history
gAtt@Conventions = Conventions
gAtt@Source      = Source
gAtt@title       = title

;-------------------------------------------------------------------------------
print_clock("writing "+fn_out)
;-------------------------------------------------------------------------------

system("/bin/rm -f "+fn_out)   ; clobber any previously created file
fh_out = addfile(fn_out ,"c")  ; open output netCDF file

setfileoption(fh_out,"DefineMode",True) ;---------------------------------------

dimNames = (/"n"    ,"ni"   ,"nj", "nv"  /)
dimSizes = (/ ni*nj , ni    , nj  , nv   /)
dimUnlim = (/False  ,False, False, False /)
filedimdef(fh_out,dimNames,dimSizes,dimUnlim)

fileattdef    (fh_out,gAtt)           ; add global attributes

filevardef(fh_out,"xc"   ,typeof(xc)   , (/"nj","ni"/) )
filevardef(fh_out,"yc"   ,typeof(yc)   , (/"nj","ni"/) )
filevardef(fh_out,"xv"   ,typeof(xv)   , (/"nj","ni","nv"/) )
filevardef(fh_out,"yv"   ,typeof(yv)   , (/"nj","ni","nv"/) )
filevardef(fh_out,"mask" ,typeof(dmask), (/"nj","ni"/) )
; filevardef(fh_out,"sort" ,typeof(sort) , (/"nj","ni"/) )
filevardef(fh_out,"area" ,typeof(area) , (/"nj","ni"/) )
; filevardef(fh_out,"fracl",typeof(fracl), (/"nj","ni"/) )

filevarattdef(fh_out,"xc"   ,xc)
filevarattdef(fh_out,"yc"   ,yc)
filevarattdef(fh_out,"xv"   ,xv)
filevarattdef(fh_out,"yv"   ,yv)
filevarattdef(fh_out,"mask" ,dmask)
; filevarattdef(fh_out,"sort" ,sort)
filevarattdef(fh_out,"area" ,area)
;filevarattdef(fh_out,"fracl",fracl)

setfileoption(fh_out,"DefineMode",False) ;---------------------------------------

fh_out->xc    = (/xc    /)
fh_out->yc    = (/yc    /)
fh_out->xv    = (/xv    /)
fh_out->yv    = (/yv    /)
fh_out->mask  = (/dmask /)
; fh_out->sort  = (/sort  /)
fh_out->area  = (/area  /)
;fh_out->fracl = (/fracl /)

;=========================================================================================
;=========================================================================================
; make scrip/esmf domain file (fields are 1d vectors)
;=========================================================================================

;-------------------------------------------------------------------------------
print_clock("create data")
;-------------------------------------------------------------------------------
grid_size    = ni*nj
grid_rank    = 2
grid_corners = 4

s_yc   = new( (/grid_size/)             , "double")
s_xc   = new( (/grid_size/)             , "double")
s_yv   = new( (/grid_size,grid_corners/), "double")
s_xv   = new( (/grid_size,grid_corners/), "double")
s_area = new( (/grid_size/)             , "double")
s_mask = new( (/grid_size/)             , "integer")
s_dims = new( (/grid_rank/)             , "integer")

s_dims(0) = ni
s_dims(1) = nj

n=-1
do j=0,nj-1
do i=0,ni-1
   n=n+1
   s_yc  (n)   = yc   (j,i)
   s_yv  (n,0) = yv   (j,i,0)
   s_yv  (n,1) = yv   (j,i,1)
   s_yv  (n,2) = yv   (j,i,2)
   s_yv  (n,3) = yv   (j,i,3)
   s_xc  (n)   = xc   (j,i)
   s_xv  (n,0) = xv   (j,i,0)
   s_xv  (n,1) = xv   (j,i,1)
   s_xv  (n,2) = xv   (j,i,2)
   s_xv  (n,3) = xv   (j,i,3)
   s_area(n)   = area (j,i)
   s_mask(n)   = dmask(j,i)
end do
end do

;-------------------------------------------------------------------------------
print_clock("create meta-data")
;-------------------------------------------------------------------------------

gAtt@Conventions = "CESM/SCRIP/ESMF mapping file domain specification"

s_yc@units = "degrees"
s_xc@units = "degrees"
s_yv@units = "degrees"
s_xv@units = "degrees"

s_area@units= "radians^2"
s_mask@note = "unitless"
s_mask@convention = "0 <=> inactive cell"
s_dims@note = "dimensions of underlying multi-dimensional array"

delete(s_dims@_FillValue)
delete(s_yc@_FillValue)
delete(s_xc@_FillValue)

delete(s_yv@_FillValue)
delete(s_xv@_FillValue)

delete(s_xc@bounds)
delete(s_yc@bounds)
delete(s_mask@_FillValue)
delete(s_mask@coordinates)
delete(s_area@_FillValue)
delete(s_area@coordinates)

;=========================================================================================
print_clock("done. ")
;=========================================================================================

quit

