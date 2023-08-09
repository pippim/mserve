#!/bin/bash

# Touch and modify 3 CDs in ~/Music/Compiliations

cd ~/Music/Compilations
prefix="Greatest Hits Of The 80's [Disc "
for f in "$prefix""1]"/*.m4a "$prefix""2]"/*.m4a "$prefix""3]"/*.m4a ; do
  echo "more stuff" >> "$f"
  touch -m -d "40 years ago" "$f"
done


# Touch only 3 CDs in ~/Music/Compiliations
prefix2="Glad All Over"
prefix3="Recharged"
prefix4="The Lost Boys"
for f in "$prefix2"/*.m4a "$prefix3"/*.m4a "$prefix4"/*.m4a ; do
  touch -m -d "4 hours ago" "$f"
done

echo $(date)
