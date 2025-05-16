wget -q --post-data="results_as_file=1&sensor_id=6&dtid=1123&sdate=1997-09-04%2000:00:00&edate=2025-05-13%2023:59:59&subType=1&addurl=1&prod_id=chlor_a&resolution_id=9km&period=MC" \
  -O - https://oceandata.sci.gsfc.nasa.gov/api/file_search |
  grep 'L3m.MC.CHL.chlor_a.9km' |
  wget --user=manishvenu --ask-password --auth-no-challenge=on -N --wait=0.5 --random-wait -i -
