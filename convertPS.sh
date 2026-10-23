postscript="$1"
basename=$(basename "$postscript" .ps)

echo "Converting $postscript to $basename.jpg"

gs -sDEVICE=jpeg \
   -dJPEGQ=100 \
   -dNOPAUSE \
   -dBATCH \
   -dSAFER \
   -dAutoRotatePages=/None \
   -r300 \
   -sOutputFile="${basename}.jpg" \
   -c "<</Orientation 3>> setpagedevice" \
   -f "$postscript"