import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import warnings
warnings.filterwarnings("ignore")

ds = xr.open_dataset(
    "/glade/derecho/scratch/manishrv/archive/demo-case-1/ocn/hist/demo-case-1.mom6.h.sfc.2020-01.nc",
    decode_timedelta=False,
)

tos = ds["tos"]

lon = ds.xh.values
lat = ds.yh.values
# Convert lon from 0-360 to -180-180 for cartopy
lon_plot = lon - 360.0

vmin = float(np.nanpercentile(tos.values, 2))
vmax = float(np.nanpercentile(tos.values, 98))

proj = ccrs.PlateCarree()
fig, ax = plt.subplots(
    figsize=(10, 7),
    subplot_kw={"projection": proj},
    facecolor="#0a0a1a",
)
ax.set_facecolor("#0a0a1a")
ax.set_extent([lon_plot.min() - 0.2, lon_plot.max() + 0.2,
               lat.min() - 0.2, lat.max() + 0.2], crs=proj)

cmap = plt.cm.turbo

im = ax.pcolormesh(
    lon_plot, lat, tos.isel(time=0).values,
    cmap=cmap, vmin=vmin, vmax=vmax,
    shading="auto", transform=proj,
)

# Land on top
ax.add_feature(cfeature.LAND.with_scale("10m"), facecolor="white", zorder=4)
ax.add_feature(cfeature.COASTLINE.with_scale("10m"), edgecolor="#aaa", linewidth=0.8, zorder=5)
ax.add_feature(cfeature.BORDERS.with_scale("10m"), edgecolor="#aaa", linewidth=0.5, zorder=5)

gl = ax.gridlines(draw_labels=True, linewidth=0.4, color="gray", alpha=0.5, linestyle="--")
gl.top_labels = False
gl.right_labels = False
gl.xlabel_style = {"color": "white", "fontsize": 9}
gl.ylabel_style = {"color": "white", "fontsize": 9}

cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.04)
cbar.set_label("SST (°C)", color="white", fontsize=12)
cbar.ax.yaxis.set_tick_params(color="white")
plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color="white")

title = ax.set_title("", color="white", fontsize=14, pad=12)

def update(i):
    t = ds.time.values[i]
    date_str = str(t)[:10]
    im.set_array(tos.isel(time=i).values.ravel())
    title.set_text(f"Sea Surface Temperature  |  {date_str}")
    return im, title

HOLD_SECS = 1
FPS = 24
# Repeat each data frame FPS*HOLD_SECS times so the video encodes cleanly
total_frames = len(ds.time) * FPS * HOLD_SECS

def update_held(frame):
    return update(frame // (FPS * HOLD_SECS))

ani = animation.FuncAnimation(
    fig, update_held, frames=total_frames, interval=1000 // FPS, blit=False
)

out = "/glade/u/home/manishrv/documents/croc/dev/sst_demo.mp4"
writer = animation.FFMpegWriter(fps=FPS, bitrate=3000, extra_args=["-vcodec", "libx264", "-pix_fmt", "yuv420p"])
ani.save(out, writer=writer, dpi=180)
plt.close()
print(f"Saved: {out}")
