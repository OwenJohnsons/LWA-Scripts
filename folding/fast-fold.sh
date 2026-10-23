fil=$1

echo "" 
echo "Processing $fil" 

basename=$(basename "$fil" .fil)
basepath=$(dirname "$fil")
echo "Base path: $basepath, Base name: $basename"

folding_dir="$basepath/folding"
mkdir -p "$folding_dir"
cd "$folding_dir" || exit 1
echo "Changed directory to: $folding_dir"

rfifind -zapchan 0:693 -time 1.0 "$fil" -o "${basename}_mask"
rfifind -zapchan 0:693 -time 1.0 "$fil" -zerodm -mask "$folding_dir/${basename}_mask_rfifind.mask" -o "${basename}_0mask"

# ADD JB reference script 
DM=56.7109
F0=29.5357554730

echo "Using DM: $DM, F0: $F0"
P=$(awk "BEGIN {print 1.0 / $F0}")
echo "Calculated period: $P seconds"

# prepfold -noxwin -ignorechan 0:693 -f "$F0" -dm "$DM" "$fil" -mask "$folding_dir/${basename}_0mask_rfifind.mask" -zerodm -topo -nsub 3072 -o "${basename}_0fold_fullband"
# prepfold -noxwin -ignorechan 0:693 -f "$F0" -dm "$DM" "$fil" -mask "$folding_dir/${basename}_0mask_rfifind.mask" -zerodm -topo -nsub 3072 -nopdsearch -ndmfact 4 -npfact 10 -n 256 -o "${basename}_0fold_fullband"